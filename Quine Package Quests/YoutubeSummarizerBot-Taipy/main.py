import os
import sys

from taipy.gui import Gui, State, notify
import openai
from langchain_community.document_loaders import YoutubeLoader
from ai_utils import summarize_by_map_reduce
from copy import deepcopy

client = None
default_conversation = [
    "Who are you?",
    "Hi! I am Youtube Summarizer chatbot. \nPlease enter your Youtube link and I will summarize it for you!",
]
conversation = {"Conversation": deepcopy(default_conversation)}
current_user_message = ""
current_youtube_link = ""
past_conversations = []
selected_conv = None
selected_row = [1]


def on_init(state: State) -> None:
    """
    Initialize the app.

    Args:
        - state: The current state of the app.
    """
    state.conversation = {"Conversation": deepcopy(default_conversation)}
    state.current_user_message = ""
    state.past_conversations = []
    state.selected_conv = None
    state.selected_row = [1]


def request(state: State, messages) -> str:
    """
    Send a prompt to the GPT-3 API and return the response.

    Args:
        - state: The current state of the app.
        - prompt: The prompt to send to the API.

    Returns:
        The response from the API.
    """
    response = state.client.chat.completions.create(
        messages=messages,
        model="gpt-4",
    )
    return response.choices[0].message.content


def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the context.

    Args:
        - state: The current state of the app.
    """
    pass


def send_youtube_link(state: State) -> None:
    """
    Send the youtube link to the API and update the context.

    Args:
        - state: The current state of the app.
    """
    try:
        notify(state, "info", "Sending message...")
        question = f"Can you summarize the video at {state.current_youtube_link}?"

        conv = state.conversation._dict.copy()
        conv["Conversation"] += [question]
        state.conversation = conv

        loader = YoutubeLoader.from_youtube_url(
            state.current_youtube_link,
            add_video_info=False,
            language=["en", "vi"],
            translation="en",
        )
        state.current_youtube_link = ""
        docs = loader.load()
        answer = summarize_by_map_reduce(docs)

        conv = state.conversation._dict.copy()
        conv["Conversation"] += [answer]
        state.conversation = conv
        notify(state, "success", "Response received!")

        state.selected_row = [len(state.conversation["Conversation"]) + 1]

    except Exception as e:
        pass


def style_conv(state: State, idx: int, row: int) -> str:
    """
    Apply a style to the conversation table depending on the message's author.

    Args:
        - state: The current state of the app.
        - idx: The index of the message in the table.
        - row: The row of the message in the table.

    Returns:
        The style to apply to the message.
    """
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_message"
    else:
        return "gpt_message"


def on_exception(state, function_name: str, ex: Exception) -> None:
    """
    Catches exceptions and notifies user in Taipy GUI

    Args:
        state (State): Taipy GUI state
        function_name (str): Name of function where exception occured
        ex (Exception): Exception
    """
    notify(state, "error", f"An error occured in {function_name}: {ex}")


def reset_chat(state: State) -> None:
    """
    Reset the chat by clearing the conversation.

    Args:
        - state: The current state of the app.
    """
    state.past_conversations = state.past_conversations + [
        [len(state.past_conversations), state.conversation]
    ]
    state.conversation = {"Conversation": deepcopy(default_conversation)}
    state.selected_row = [len(state.conversation["Conversation"]) + 1]


def tree_adapter(item: list) -> [str, str]:
    """
    Converts element of past_conversations to id and displayed string

    Args:
        item: element of past_conversations

    Returns:
        id and displayed string
    """
    identifier = item[0]
    if len(item[1]["Conversation"]) > 3:
        return (identifier, item[1]["Conversation"][3][:50] + "...")
    return (item[0], "Empty conversation")


def select_conv(state: State, var_name: str, value) -> None:
    """
    Selects conversation from past_conversations

    Args:
        state: The current state of the app.
        var_name: "selected_conv"
        value: [[id, conversation]]
    """
    state.conversation = state.past_conversations[value[0][0]][1]
    state.selected_row = [len(state.conversation["Conversation"]) + 1]


past_prompts = []

page = """
<|layout|columns=300px 1|
<|part|render=True|class_name=sidebar|
# Youtube **Summarizer**{: .color-primary} # {: .logo-text}
<|New Conversation|button|class_name=fullwidth plain|id=reset_app_button|on_action=reset_chat|>
### Previous activities ### {: .h5 .mt2 .mb-half}
<|{selected_conv}|tree|lov={past_conversations}|class_name=past_prompts_list|multiple|adapter=tree_adapter|on_change=select_conv|>
|>

<|part|render=True|class_name=p2 align-item-bottom table|
<|{conversation}|table|style=style_conv|show_all|width=100%|selected={selected_row}|rebuild|>
<|part|class_name=card mt1|
<|{current_youtube_link}|input|label=Paste your Youtube link...|on_action=send_youtube_link|class_name=fullwidth|>
|>
|>
|>
"""

if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
    elif len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        raise ValueError(
            "Please provide the OpenAI API key as an environment variable OPENAI_API_KEY or as a command line argument."
        )

    client = openai.Client(api_key=api_key)

    Gui(page).run(
        debug=True, dark_mode=True, use_reloader=True, title="Youtube Summarizer"
    )
