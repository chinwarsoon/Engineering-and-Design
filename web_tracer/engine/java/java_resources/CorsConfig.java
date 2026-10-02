package com.webtracer.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * CorsConfig — lets the browser carry the W3C `traceparent` header across the CORS preflight
 * (workplan T17 / T33). If the preflight does NOT allow `traceparent`, the browser drops it and
 * the cross-layer correlation link is lost (downgrade to url_time_window, confidence <= 0.8).
 *
 * NOTE: the Web Tracer backend itself already sets `allow_headers = "*"`, so for our own target
 * the downgrade never triggers — this template is for a *separate* business backend that must
 * also permit the header.
 */
@Configuration
public class CorsConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOriginPatterns("*")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        // allow the propagation header so the trace link survives the preflight
                        .allowedHeaders("*", "traceparent", "tracestate")
                        .exposedHeaders("traceparent", "tracestate")
                        .allowCredentials(true);
            }
        };
    }
}
