import re
import sys
import logging
import pytz
from datetime import datetime
from langchain.llms import OpenAI
from moments.agent import Agent
from moments.moment import (
    Moment,
    Participant,
    Self,
    Context,
    Instructions,
    Example,
    Begin,
)

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s | %(message)s"
)
LOG = logging.getLogger(__name__)

llm = OpenAI(model_name="text-davinci-003", n=2, best_of=2)


class LlmOpenAiAgent(Agent):
    def before(self: "LlmOpenAiAgent", moment: Moment):
        # Add context if not already present.
        is_context_added = False
        for occurrence in moment.occurrences:
            if isinstance(occurrence, Context):
                is_context_added = True
                break

        if not is_context_added:
            tz = pytz.timezone("America/Los_Angeles")
            current_time = datetime.now(tz)
            moment.occurrences.append(
                Context('```time: "' + current_time.strftime("%I:%M %p") + '"```')
            )

    def do(self: "LlmOpenAiAgent", moment: Moment):
        # Add final "Self:" for agent to speak.
        prompt = str(moment) + "Self: "
        # Complete with langchain
        response = llm(prompt.strip())
        line = response.split("\n")[0].strip()
        print(f"-->{line}<--")
        if not re.match(r"^Self:\s+(\((.*)\)\s+)?\"(.+)\"$", line):
            # Try to fix it
            if not line.startswith('"'):
                line = '"' + line
            if not line.endswith('"'):
                line = line + '"'
            if not line.startswith("Self: "):
                line = "Self: " + line
        moment.occurrences.append(Self.parse(line))

    def after(self: "LlmOpenAiAgent", moment: Moment):
        pass
