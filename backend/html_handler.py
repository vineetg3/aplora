from bs4 import BeautifulSoup, Tag
from difflib import HtmlDiff

class HTMLHandler:
    """Handles operations on HTML using BeautifulSoup."""

    allowed_attrs = ['class', 'id', 'aria-describedby', 'aria-label', 'aria-haspopup', 'aria-required', 'data-automation-id',"autocomplete","name","type","value","required","role"]

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")
    
    # def tags_to_list(self):
    #     '''
    #     Sample output:
    #     [
    #         {
    #             'key': 'input_1',
    #             'aria-label': 'Male, Gender',
    #             'id': 'gender-male',
    #             'idx': 0
    #         },
    #         {
    #             'key': 'select_1',
    #             'aria-label': 'Select your country',
    #             'id': 'country-selector',..
    #         },
    #         ...
    #     ]
    #     '''
    #     # Initialize the result list and counters for each tag type
    #     result_list = []
    #     input_count = 0
    #     select_count = 0
    #     textarea_count = 0
    #     btn_count = 0

    #     # Helper function to sanitize elements
    #     def sanitize_element(element):
    #         sanitized = {attr: element.get(attr) for attr in HTMLHandler.allowed_attrs if element.has_attr(attr)}
    #         return sanitized

    #     idx = 0

    #     # Find all desired tags in the order they appear in the DOM
    #     for tag in self.soup.find_all(['input', 'select', 'textarea', 'button']):
    #         tag_dict = sanitize_element(tag)

    #         if tag.name == 'input':
    #             input_count += 1
    #             key = f"input_{input_count}"
    #             tag_type='input'
    #         elif tag.name == 'select':
    #             select_count += 1
    #             key = f"select_{select_count}"
    #             tag_type='select'
    #         elif tag.name == 'textarea':
    #             textarea_count += 1
    #             key = f"textarea_{textarea_count}"
    #             tag_type='textarea'
    #         elif tag.name == 'button':
    #             btn_count += 1
    #             key = f"button_{btn_count}"
    #             tag_type='button'
    #         else:
    #             continue  # Skip unsupported tags

    #          # Find nearest text above
    #         text_above = []
    #         for prev in tag.find_all_previous(string=True, limit=3):
    #             stripped = prev.strip()
    #             if stripped:
    #                 text_above.append(stripped[:min(120,len(stripped))])
    #         text_above.reverse()  # Reverse to maintain top-to-bottom order

    #         # Find nearest text below
    #         text_below = []
    #         for next_ in tag.find_all_next(string=True, limit=3):
    #             stripped = next_.strip()
    #             if stripped:
    #                 text_below.append(stripped[:min(120,len(stripped))])

    #         tag_dict["text_above_htmltag"] = text_above
    #         tag_dict["text_below_htmltag"] = text_below
    #         tag_dict["key"] = key
    #         tag_dict["idx"] = idx
    #         tag_dict["tag_type"] = tag_type
    #         idx += 1
    #         result_list.append(tag_dict)

    #     return result_list

    def tags_to_list(self):
        '''
        Sample output:
        [
            {
                'key': 'input_1',
                'aria-label': 'Male, Gender',
                'id': 'gender-male',
                'idx': 0,
                'tag_type': 'input',
                'text_above_htmltag': [...],
                'text_below_htmltag': [...]
            },
            {
                'key': 'select_1',
                'aria-label': 'Select your country',
                'id': 'country-selector',
                'idx': 1,
                'tag_type': 'select',
                'options': [
                    {'value': 'us', 'text': 'United States'},
                    {'value': 'ca', 'text': 'Canada'},
                    ...
                ],
                'text_above_htmltag': [...],
                'text_below_htmltag': [...]
            },
            ...
        ]
        '''
        # Initialize the result list and counters for each tag type
        result_list = []
        input_count = 0
        select_count = 0
        textarea_count = 0
        btn_count = 0

        # Helper function to sanitize elements
        def sanitize_element(element):
            sanitized = {attr: element.get(attr) for attr in HTMLHandler.allowed_attrs if element.has_attr(attr)}
            return sanitized

        idx = 0

        # Find all desired tags in the order they appear in the DOM
        for tag in self.soup.find_all(['input', 'select', 'textarea', 'button']):
            tag_dict = sanitize_element(tag)

            if tag.name == 'input':
                input_count += 1
                key = f"input_{input_count}"
                tag_type = 'input'
            elif tag.name == 'select':
                select_count += 1
                key = f"select_{select_count}"
                tag_type = 'select'

                # Add `options` key for <select> tags
                options = []
                for option in tag.find_all('option'):
                    option_data = {
                        'value': option.get('value', ''),
                        'text': option.text.strip()
                    }
                    options.append(option_data)

                tag_dict["select_options"] = options

            elif tag.name == 'textarea':
                textarea_count += 1
                key = f"textarea_{textarea_count}"
                tag_type = 'textarea'
            elif tag.name == 'button':
                btn_count += 1
                key = f"button_{btn_count}"
                tag_type = 'button'
            else:
                continue  # Skip unsupported tags

            # Find nearest text above
            text_above = []
            for prev in tag.find_all_previous(string=True, limit=3):
                stripped = prev.strip()
                if stripped:
                    text_above.append(stripped[:min(120, len(stripped))])
            text_above.reverse()  # Reverse to maintain top-to-bottom order

            # Find nearest text below
            text_below = []
            for next_ in tag.find_all_next(string=True, limit=3):
                stripped = next_.strip()
                if stripped:
                    text_below.append(stripped[:min(120, len(stripped))])

            # Add metadata for all tags
            tag_dict["text_above_htmltag"] = text_above
            tag_dict["text_below_htmltag"] = text_below
            tag_dict["key"] = key
            tag_dict["idx"] = idx
            tag_dict["tag_type"] = tag_type

            idx += 1
            result_list.append(tag_dict)

        return result_list

    def get_input_elements(self):
        """
        Extract all input elements from the HTML.
        :return: List of input elements as dictionaries (attributes only).
        """
        inputs = self.soup.find_all("input")
        return [dict(inp.attrs) for inp in inputs]
    
    def get_element_with_text(self, search_text: str):
        """
        Get the element containing a given text and its allowed attributes.
        :param search_text: Text to search for.
        :return: Dictionary of allowed attributes and related information, or None if not found.
        """
        element = self.soup.find(string=lambda text: search_text.strip()==text.strip() if text else False)
        if not element:
            return None

        # Ensure the element is a Tag, not a NavigableString
        if isinstance(element, str):
            element = element.parent

        result = {}

        # Get allowed attributes
        for attr in self.allowed_attrs:
            if element.has_attr(attr):
                attr_value = element[attr]
                # Convert to list if it's a space-separated string for class
                if attr == 'class' and isinstance(attr_value, str):
                    result[attr] = attr_value.split()
                else:
                    result[attr] = attr_value

        # Add additional fields
        result.update({
            'key': f"element_{element.sourceline if hasattr(element, 'sourceline') else 0}",  # Example key generation
            'idx': element.sourceline if hasattr(element, 'sourceline') else 0,
            'tag_type': element.name,
            'is_relevant_or_required': 'yes' if element.get('aria-required') == 'true' else 'no',
            'text_value': search_text,
            'is_filled': 'yes' if element.get('value') else 'no',
            'general_input_group': 'dropdown' if element.get('aria-haspopup') == 'true' else '',
            'description': f"Element containing the text: {search_text}"
        })

        return result

    def get_parent_of_text(self, search_text: str):
        """
        Get the parent element and its attributes of the first occurrence of a given text.
        :param search_text: Text to search for.
        :return: Dictionary of allowed attributes and related information, or None if not found.
        """
        element = self.soup.find(string=lambda text: search_text.strip()==text.strip() if text else False)
        if not element or not element.parent:
            return None

        parent = element.parent
        result = {}

        # Get allowed attributes
        for attr in self.allowed_attrs:
            if parent.has_attr(attr):
                attr_value = parent[attr]
                # Convert to list if it's a space-separated string for class
                if attr == 'class' and isinstance(attr_value, str):
                    result[attr] = attr_value.split()
                else:
                    result[attr] = attr_value

        # Get text above the tag (previous siblings' text)
        text_above = []
        for sibling in parent.find_previous_siblings():
            if sibling.string and sibling.string.strip():
                text_above.append(sibling.string.strip())
        result['text_above_htmltag'] = list(reversed(text_above))

        # Get text below the tag (next siblings' text)
        text_below = []
        for sibling in parent.find_next_siblings():
            if sibling.string and sibling.string.strip():
                text_below.append(sibling.string.strip())
        result['text_below_htmltag'] = text_below

        # Add additional fields
        result.update({
            'key': f"input_{len(result.get('text_above_htmltag', []))}", # Example key generation
            'idx': parent.sourceline if hasattr(parent, 'sourceline') else 0,
            'tag_type': parent.name,
            'is_relevant_or_required': 'yes' if parent.get('aria-required') == 'true' else 'no',
            'text_value': search_text,
            'is_filled': 'yes' if parent.get('value') else 'no',
            'general_input_group': 'dropdown' if parent.get('aria-haspopup') == 'true' else '',
            'description': f"A {parent.name} element for {search_text}"
        })

        return result

    def get_lines_of_text(self):
        return [text.strip() for text in self.soup.stripped_strings]
    

    @classmethod
    def compare_html(cls, old_handler, new_handler):
        """
        Compares two HTMLHandler objects and finds lines of text
        that are new in the new_handler compared to old_handler.
        """
        old_lines = set(old_handler.get_lines_of_text())
        new_lines = set(new_handler.get_lines_of_text())

        new_in_new_html = new_lines - old_lines
        return new_in_new_html