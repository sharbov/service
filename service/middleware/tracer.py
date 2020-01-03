from contextlib import contextmanager

from flask import request, g
from jaeger_client import Config
from jaeger_client.codecs import TextCodec


class Tracer:
    def __init__(self):
        """Initialize Jaeger tracer."""
        self.config = None
        self.jaeger = None
        self.codec = TextCodec()

    def init_app(self, app):
        """Initialize app to trace requests."""
        if not app.config["TRACER_ENABLED"]:
            return

        self.config = Config(
            config={
                "logging": False,
                "sampler": {"type": "const", "param": 1},
                "local_agent": {"reporting_host": app.config["TRACER_HOST"]},
            },
            service_name=app.config["SERVICE_NAME"],
        )
        self.jaeger = self.config.new_tracer()
        app.before_request(self.start_request_span)
        app.after_request(self.end_request_span)

    def start_request_span(self):
        """Start span before request function is called."""
        span_context = self.extract_context(request.headers)
        name = request.method + " " + request.path
        g.span = self.jaeger.start_span(name, child_of=span_context)
        g.carrier = self.inject_context()

    @staticmethod
    def end_request_span(response):
        """Stop span after request function is called."""
        g.span.finish()
        return response

    def extract_context(self, carrier):
        """Extract span context from the carrier info.

        :param dict carrier: carrier info.
        :return SpanContext: the span context.
        """
        return self.codec.extract(carrier=carrier)

    def inject_context(self, span_context=None, carrier=None):
        """Inject span context to the carrier info.

        :param SpanContext span_context: the span context.
        :param dict carrier: carrier info.
        """
        carrier = carrier if carrier else {}
        span_context = span_context if span_context else g.span.context
        self.codec.inject(span_context=span_context, carrier=carrier)
        return carrier

    @contextmanager
    def start_span(self, name, carrier=None):
        """Span context manager.

        :param str name: span name.
        :param dict carrier: carrier info.
        """
        span_context = self.extract_context(carrier) if carrier else None
        with self.jaeger.start_span(name, child_of=span_context):
            yield


tracer = Tracer()
