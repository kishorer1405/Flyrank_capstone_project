from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ============================================================
# Widget Field
# ============================================================

class WidgetField(BaseModel):

    name: str = Field(
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]{0,39}$"
    )

    label: str = Field(
        min_length=1,
        max_length=80
    )

    type: Literal[
        "text",
        "email",
        "tel",
        "textarea",
    ] = "text"

    required: bool = True

    placeholder: str = Field(
        default="",
        max_length=120
    )


# ============================================================
# Widget Base
# ============================================================

class WidgetBase(BaseModel):

    title: str = Field(
        min_length=2,
        max_length=120
    )

    description: str = Field(
        default="",
        max_length=500
    )

    widget_type: Literal[
        "signup",
        "contact",
        "cta",
        "popover",
    ] = "signup"

    fields: list[WidgetField] = Field(
        min_length=1,
        max_length=10
    )

    button_text: str = Field(
        default="Submit",
        min_length=1,
        max_length=80
    )

    display_options: dict = Field(
        default_factory=dict
    )

    is_active: bool = True

    # --------------------------------------------------------
    # Validate Unique Field Names
    # --------------------------------------------------------

    @field_validator("fields")
    @classmethod
    def unique_field_names(cls, value):

        names = [
            field.name
            for field in value
        ]

        if len(names) != len(set(names)):
            raise ValueError(
                "Field names must be unique"
            )

        return value


# ============================================================
# Widget Create
# ============================================================

class WidgetCreate(WidgetBase):
    pass


# ============================================================
# Widget Update
# ============================================================

class WidgetUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=120
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    widget_type: Literal[
        "signup",
        "contact",
        "cta",
        "popover",
    ] | None = None

    fields: list[WidgetField] | None = Field(
        default=None,
        min_length=1,
        max_length=10
    )

    button_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=80
    )

    display_options: dict | None = None

    is_active: bool | None = None


# ============================================================
# Widget Response
# ============================================================

class WidgetResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str

    title: str

    description: str

    widget_type: Literal[
        "signup",
        "contact",
        "cta",
        "popover",
    ]

    fields: list[WidgetField]

    button_text: str

    display_options: dict

    is_active: bool

    version: int

    embed_snippet: str


# ============================================================
# Public Widget Configuration
# ============================================================

class PublicWidgetConfig(BaseModel):

    id: str

    title: str

    description: str

    widget_type: str

    fields: list[WidgetField]

    button_text: str

    display_options: dict

    version: int

    submission_url: str