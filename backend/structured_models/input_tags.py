from typing import List, Optional, Literal, Dict, Union

from pydantic import BaseModel, Field


class InputTagDescription(BaseModel):
    """defines the structure for describing HTML input tags. Each field provides specific instructions for accurate and context-aware processing"""

    is_relevant_or_required: Literal["yes","no"] = Field(description="Set yes if its a required field. Set to yes if the field is relevant to the context. Mark yes if aria-required exists. For radio buttons, make only one relevant. Buttons of type submit are not relevant.")
    # general_input_group: str = Field(None,
    #             description="Classify tags as dropdown, input text, radiobutton, button, textarea,checkbox. Tags with aria-haspopup are dropdowns. Tags with type=text are input text, unless similar options suggest a dropdown. Prefer dropdown in ambiguous cases."
    #         )
    key: str = Field(description="unique key that should be picked up from the input tag list")
    text_value: Union[None | str] = Field(description="Please fill sensible relevent text here based on your understanding of what the html tag would want. Fill this field with the relevant output and do not keep None. \
                                                        Only get it from the context document. Verify by summarizing the html tag and its attributes.")
    is_filled:  Literal["yes","no"] = Field(description="Ignore this field. Default is no",      default="no",exclude=True)
    select_option_value: Union[None | str] = Field(description="""Look at the description of the tag and select a suitable value from the select_options key.For example if select_options=[ \
    {
        "value": "Male",
        "text": "man"}, {
        "value": "Female",
        "text": "woman"
    } And you decide that it should be a Male, so you output the value: Male.""")


class InputTagDescriptionList(BaseModel):
    """Extracted data about input tags and relevancy from the appended document"""

    # Creates a model so that we can extract multiple entities.
    tags: List[InputTagDescription]