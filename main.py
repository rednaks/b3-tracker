import datetime
import json
import pickle
from enum import Enum
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from pydantic.fields import Field


@dataclass
class State:
    content: str = Field(default_factory=str)
    errors: List[Tuple[str, str]] = Field(default_factory=list)


class Event(str, Enum):
    CHANGED = "changed"
    ERROR = "error"


EVENT_COLOR = {
    str(Event.CHANGED): "8247894",
    str(Event.ERROR): "14177041",
}


@dataclass
class Config:
    tracking_id: str
    cin_or_passport_number: str
    webhook_url: str


class DiscordWebhookEmbed(BaseModel):
    title: str
    description: str
    color: str
    timestamp: Optional[str] = Field(default_factory=str)


class DiscordWebhookPayload(BaseModel):
    username: str
    content: str = Field(default_factory=str)
    embeds: List[DiscordWebhookEmbed] = Field(default_factory=list)


def load_state(path: str = "./.state") -> State:
    with open(path, mode="rb") as f:
        des = pickle.Unpickler(f).load()
        return des


def load_config() -> Config:
    with open("./config.json", "r") as fp:
        return Config(**json.load(fp))


def save_state(state: State, path: str = "./.state"):
    with open(path, "wb") as f:
        pickle.Pickler(f).dump(state)


def get_b3_status(config: Config):
    data = {
        "data[Demande][id_transaction]": config.tracking_id,
        "data[Demande][numdocid]": config.cin_or_passport_number,
    }

    response = requests.post(
        "https://b3.interieur.gov.tn/suivi",
        data=data,
        verify=False,
    )
    return response


def notify_discord(webhook_url: str, state: State, event: Event):
    try:

        payload = DiscordWebhookPayload(username="B3 Tracker")

        color = EVENT_COLOR[str(event)]

        if event == Event.CHANGED:
            payload.embeds.append(
                DiscordWebhookEmbed(
                    title="The Tracking status just changed!",
                    description=state.content,
                    color=color,
                )
            )
        elif event == Event.ERROR:
            payload.content = "Reached errors threshold !"
            for error in state.errors:
                payload.embeds.append(
                    DiscordWebhookEmbed(
                        title="",
                        description=error[1],
                        color=color,
                        timestamp=error[0],
                    )
                )

        requests.post(webhook_url, json=payload.dict())
    except Exception as e:
        print(f"Unable to notify discord: {e}")


def parse_status(html):
    soup = BeautifulSoup(html, "html.parser")
    res = soup.select("div.alert-box:nth-child(1)")
    status = str(res[0].contents[0]).strip()
    print(status)
    return status


if __name__ == "__main__":
    # load state
    state = State()
    try:
        state = load_state()
        print(f"loaded saved state : {state}")
    except FileNotFoundError:
        save_state(state)
        print(f"created new state : {state}")

    config = load_config()
    try:
        response = get_b3_status(config)
    except Exception as e:
        state.errors.append((datetime.datetime.now().isoformat(), str(e)))
        save_state(state)
        raise Exception from e

    if response.ok:
        html = response.text
        try:
            content = parse_status(html)
            if state.content != content:
                print("diffrent content, sending a notification to discord")
                state.content = content
                state.errors = []
                notify_discord(config.webhook_url, state, Event.CHANGED)

        except Exception as e:
            state.errors.append((datetime.datetime.now().isoformat(), str(e)))

    else:
        state.errors.append(
            (
                datetime.datetime.now().isoformat(),
                f"code: {response.status_code}, content: {response.text}",
            )
        )

    if len(state.errors) >= 3:
        print("There are some errors, please check logs")
        notify_discord(config.webhook_url, state, Event.ERROR)
        state.errors = []

    save_state(state)
