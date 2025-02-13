import datetime
import json5
import logging
import streamlit as st
import pathlib
from typing import Union
from config import slide_creator_config as config

@st.cache_data
def _load_strings() -> dict:
    """
    Load various strings to be displayed in the app.
    :return: The dictionary of strings.
    """

    with open(config.APP_STRINGS_FILE, 'r', encoding='utf-8') as in_file:
        return json5.loads(in_file.read())

@st.cache_data
def _get_prompt_template(is_refinement: bool) -> str:
    """
    Return a prompt template.

    :param is_refinement: Whether this is the initial or refinement prompt.
    :return: The prompt template as f-string.
    """

    if is_refinement:
        with open(config.REFINEMENT_PROMPT_TEMPLATE, 'r', encoding='utf-8') as in_file:
            template = in_file.read()
    else:
        with open(config.INITIAL_PROMPT_TEMPLATE, 'r', encoding='utf-8') as in_file:
            template = in_file.read()

    return template

def handle_error(error_msg: str, should_log: bool):
    """
    Display an error message in the app.

    :param error_msg: The error message to be displayed.
    :param should_log: If `True`, log the message.
    """

    if should_log:
        logger.error(error_msg)

    st.error(error_msg)

def reset_api_key():
    """
    Clear API key input when a different LLM is selected from the dropdown list.
    """

    st.session_state.api_key_input = ''

APP_TEXT = _load_strings()

# Session variables
CHAT_MESSAGES = 'chat_messages'
DOWNLOAD_FILE_KEY = 'download_file_name'
IS_IT_REFINEMENT = 'is_it_refinement'

logger = logging.getLogger(__name__)

texts = list(config.PPTX_TEMPLATE_FILES.keys())
captions = [config.PPTX_TEMPLATE_FILES[x]['caption'] for x in texts]

def build_ui():
    """
    Display the input elements for content generation.
    """

    st.title(APP_TEXT['app_name'])
    st.subheader(APP_TEXT['caption'])
    st.markdown(
        '![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fhuggingface.co%2Fspaces%2Fbarunsaha%2Fslide-deck-ai&countColor=%23263759)'  # noqa: E501
    )

    today = datetime.date.today()
    if today.month == 1 and 1 <= today.day <= 15:
        st.success(
            (
                'Wishing you a happy and successful New Year!'
                ' It is your appreciation that keeps SlideDeck AI going.'
                f' May you make some great slide decks in {today.year} ✨'
            ),
            icon='🎆'
        )

    with st.expander('Usage Policies and Limitations'):
        st.text(APP_TEXT['tos'] + '\n\n' + APP_TEXT['tos2'])

    set_up_chat_ui()

def set_up_chat_ui():
    """
    Prepare the chat interface and related functionality.
    """
    pass

def generate_slide_deck(json_str: str) -> Union[pathlib.Path, None]:
    """
    Create a slide deck and return the file path. In case there is any error creating the slide
    deck, the path may be to an empty file.

    :param json_str: The content in *valid* JSON format.
    :return: The path to the .pptx file or `None` in case of error.
    """
    pass