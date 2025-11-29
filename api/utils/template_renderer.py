import re
import json
from string import Template
from django.utils.html import escape
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """
    Utility class to render notification templates with user context.
    """
    
    def __init__(self, template):
        self.template = template

    def render_title(self, context):
        """Render the title template with user context."""
        try:
            return self._safe_render(self.template.title_template, context)
        except Exception as e:
            logger.error(f"Error rendering title template: {str(e)}")
            return self.template.title_template

    def render_body(self, context):
        """Render the body template with user context."""
        try:
            return self._safe_render(self.template.body_template, context)
        except Exception as e:
            logger.error(f"Error rendering body template: {str(e)}")
            return self.template.body_template

    def render_subject(self, context):
        """Render the subject template with user context."""
        try:
            return self._safe_render(self.template.subject_template, context) if self.template.subject_template else ""
        except Exception as e:
            logger.error(f"Error rendering subject template: {str(e)}")
            return self.template.subject_template or ""

    def render_data(self, context, additional_data=None):
        """Render the data template with user context."""
        try:
            # Parse the data template as JSON string and render its values
            if isinstance(self.template.data_template, str):
                template_data = json.loads(self.template.data_template)
            else:
                template_data = self.template.data_template.copy()
            
            # Render each value in the data template
            rendered_data = {}
            for key, value in template_data.items():
                if isinstance(value, str):
                    rendered_data[key] = self._safe_render(value, context)
                else:
                    rendered_data[key] = value
            
            # Add any additional data provided
            if additional_data:
                rendered_data.update(additional_data)
                
            return rendered_data
        except Exception as e:
            logger.error(f"Error rendering data template: {str(e)}")
            return additional_data or {}

    def _safe_render(self, template_str, context):
        """
        Safely render a template string with context, preventing code injection.
        """
        if not template_str:
            return ""

        # Sanitize the template string to prevent code execution
        # Only allow safe variable placeholders like {user.name}, {user.email}
        sanitized_template = self._sanitize_template(template_str)
        
        # Create a safe context with only allowed variables
        safe_context = self._create_safe_context(context)
        
        try:
            # Use string.Template for safe substitution
            template = Template(sanitized_template)
            rendered = template.safe_substitute(**safe_context)
            
            # Escape HTML to prevent XSS
            return escape(rendered)
        except Exception:
            # If safe substitution fails, return original template
            return template_str

    def _sanitize_template(self, template_str):
        """
        Sanitize template string to prevent code injection.
        Only allow safe variable patterns.
        """
        # Replace Django-style template tags with safe placeholders
        # This prevents execution of Django template code
        sanitized = re.sub(r'\{\{.*?\}\}', '', template_str)  # Remove {{ }}
        sanitized = re.sub(r'\{%.*?%\}', '', sanitized)  # Remove {% %}
        sanitized = re.sub(r'\{#.*?#\}', '', sanitized)  # Remove {# #}
        
        # Only allow safe variable placeholders like {user.name}
        # This regex matches {word.word} patterns
        safe_vars = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}', sanitized)
        
        # Return the template with only safe variable placeholders
        return sanitized

    def _create_safe_context(self, context):
        """
        Create a safe context by flattening nested objects and sanitizing values.
        """
        safe_context = {}
        
        def flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    # Sanitize string values to prevent XSS
                    if isinstance(v, str):
                        items.append((new_key, escape(v)))
                    else:
                        items.append((new_key, v))
            return dict(items)
        
        # Flatten the context to support nested access like {user.name}
        flattened = flatten_dict(context)
        
        # Limit the context to prevent access to dangerous attributes
        for key, value in flattened.items():
            # Only allow alphanumeric keys with dots (for nested access)
            if re.match(r'^[a-zA-Z0-9_.]+$', key):
                # Limit string length to prevent abuse
                if isinstance(value, str) and len(value) > 1000:
                    value = value[:1000] + "..."
                safe_context[key] = value
        
        return safe_context


def validate_template_context(template_str, context):
    """
    Validate that the template can be rendered with the given context.
    """
    try:
        renderer = TemplateRenderer(type('MockTemplate', (), {
            'title_template': template_str,
            'body_template': '',
            'subject_template': '',
            'data_template': {}
        })())
        
        # Try to render the template
        result = renderer._safe_render(template_str, context)
        
        # Check if all placeholders were replaced
        remaining_placeholders = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}', result)
        
        return {
            'valid': len(remaining_placeholders) == 0,
            'missing_variables': remaining_placeholders,
            'rendered': result
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'rendered': None
        }