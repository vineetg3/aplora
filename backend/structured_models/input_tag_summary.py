from typing import List, Optional, Literal, Dict, Union

from pydantic import BaseModel, Field


class InputTagSummary(BaseModel):
    """Summarizes the input tag into a description and also mentions what type of general input is that."""

    key: str = Field(description="unique key that should be picked up from the provided input tag dictionary")
    general_input_group: str = Field(None,
                description='''Classify HTML tags as dropdown, input text, radiobutton, button, textarea, or checkbox. Tags with aria-haspopup or select with option elements are dropdowns. Tags with type="text" or plain input without a type are input text unless context suggests otherwise. Use specific attributes like type="radio", type="checkbox", textarea, or role="button" to classify others. Prioritize dropdowns in ambiguous cases and explain your reasoning.'''
            )
    description: Union[None | str] = Field(description="Give in short but accurate on what is the tag trying to ask. Try to summarize from the metadata and surrounding tags.")



class InputTagSummaryList(BaseModel):
    """Extracted data about input tags from the appended document"""

    # Creates a model so that we can extract multiple entities.
    tags: List[InputTagSummary]