package com.webtracer.instrument;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;

/**
 * TracedAspect — one Spring AOP @Around advice that wraps every Controller / Service /
 * Repository method and records a span around it (workplan §7.4 / T31). Dropping this file in
 * (no edits to business code) produces NESTED method-level spans, not the flat framework-only
 * spans the vanilla OTel Java agent gives. The span carries code.namespace / code.function so
 * the Python SourceMapper (T32) and the correlation engine can resolve file:line + trace_id.
 */
@Aspect
public class TracedAspect {

    private final Tracer tracer;

    public TracedAspect(Tracer tracer) {
        this.tracer = tracer;
    }

    @Pointcut("within(@org.springframework.stereotype.Controller *)"
            + " || within(@org.springframework.web.bind.annotation.RestController *)"
            + " || within(@org.springframework.stereotype.Service *)"
            + " || within(@org.springframework.stereotype.Repository *)")
    public void businessLayer() {}

    @Around("businessLayer()")
    public Object trace(ProceedingJoinPoint pjp) throws Throwable {
        MethodSignature sig = (MethodSignature) pjp.getSignature();
        String className = sig.getDeclaringType().getName();
        String methodName = sig.getName();

        Span span = tracer.spanBuilder(className + "." + methodName)
                .setAttribute("code.namespace", className)
                .setAttribute("code.function", methodName)
                .setAttribute("span.type", "method")
                .startSpan();
        try (Scope ignored = span.makeCurrent()) {
            return pjp.proceed();
        } catch (Throwable t) {
            span.recordException(t);
            span.setStatus(io.opentelemetry.api.trace.StatusCode.ERROR);
            throw t;
        } finally {
            span.end();
        }
    }
}
