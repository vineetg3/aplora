## to be used later

from typing import List, Optional

class FormElement:
    def __init__(self, 
                 classes: Optional[List[str]] = None,
                 aria_label: Optional[str] = None,
                 element_id: Optional[str] = None,
                 aria_describedby: Optional[str] = None,
                 aria_required: Optional[str] = None,
                 autocomplete: Optional[str] = None,
                 element_type: Optional[str] = None,
                 value: Optional[str] = None,
                 text_above_htmltag: Optional[List[str]] = None,
                 text_below_htmltag: Optional[List[str]] = None,
                 key: Optional[str] = None,
                 idx: Optional[int] = None,
                 tag_type: Optional[str] = None,
                 is_relevant_or_required: Optional[str] = None,
                 text_value: Optional[str] = None,
                 is_filled: Optional[str] = None,
                 general_input_group: Optional[str] = None,
                 description: Optional[str] = None):
        self.classes = classes or []
        self.aria_label = aria_label
        self.element_id = element_id
        self.aria_describedby = aria_describedby
        self.aria_required = aria_required
        self.autocomplete = autocomplete
        self.element_type = element_type
        self.value = value
        self.text_above_htmltag = text_above_htmltag or []
        self.text_below_htmltag = text_below_htmltag or []
        self.key = key
        self.idx = idx
        self.tag_type = tag_type
        self.is_relevant_or_required = is_relevant_or_required
        self.text_value = text_value
        self.is_filled = is_filled
        self.general_input_group = general_input_group
        self.description = description

    def __repr__(self):
        return (
            f"FormElement(classes={self.classes}, aria_label={self.aria_label}, element_id={self.element_id}, "
            f"type={self.element_type}, key={self.key}, idx={self.idx}, tag_type={self.tag_type}, "
            f"is_relevant_or_required={self.is_relevant_or_required}, description={self.description})"
        )

# Example usage
# elements_data = [
#     {
#         "class": ["btn", "btn--pill"],
#         "aria-label": "Apply",
#         "type": "button",
#         "text_above_htmltag": ["Back to jobs", "Software Engineer - Early Career (2025)", "San Francisco, CA • New York, NY • United States"],
#         "text_below_htmltag": ["Apply", "Figma is growing our team of passionate people on a mission to make design accessible to all.", "Born on the Web"],
#         "key": "button_1",
#         "idx": 0,
#         "tag_type": "button",
#         "general_input_group": "button",
#         "description": "Button to apply for the Software Engineer position."
#     },
#     # Add more element data here as needed
# ]

# elements = [FormElement(**data) for data in elements_data]

# # Example printout of one element
# print(elements[0])