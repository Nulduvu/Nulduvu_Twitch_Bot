from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat

from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChannelPointsCustomRewardRedemptionAddEvent
from twitchAPI.chat import EventData, ChatCommand
from twitchAPI.type import AuthScope
from random import choice
import edge_tts
import asyncio
import pygame

pygame.init()


APP_ID: str = "n02hxwvcfk0jr8q60g6kpq5hch0gzi"
APP_SECRET: str = "afu88n9gkw1fx6a1xfktowvpu779ru"
TARGET_SCOPES: list = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.USER_READ_CHAT, AuthScope.CHANNEL_MANAGE_REDEMPTIONS]
TARGET_CHANNEL: str = "nulduvu"

VOICES: list[str] = ["fr-FR-DeniseNeural", "fr-FR-EloiseNeural", "fr-FR-HenriNeural"]

twitch_client = None

def set_twitch(twitch_instance):
    global twitch_client
    twitch_client = twitch_instance

async def on_message_read_reward(data: ChannelPointsCustomRewardRedemptionAddEvent):
    text = data.event.user_name + " dit : " + data.event.user_input
    print(text)
    voice = choice(VOICES)
    print(voice)
    output_file = "output.mp3"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

    sound = pygame.mixer.Sound(output_file)
    sound.play()
    await asyncio.sleep(sound.get_length())

async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(TARGET_CHANNEL)
    set_twitch(twitch_client)
    print("Logged in, you can start")


async def init_twitch():
    twitch = await Twitch(APP_ID, APP_SECRET)
    authenticator = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
    await authenticator.bind()

    user = await first(twitch.get_users())

    eventsub = EventSubWebsocket(twitch)
    eventsub.start()

    #await eventsub.listen_channel_chat_message(user.id, user.id, on_message)
    #await eventsub.listen_stream_online(user.id, on_stream_online)
    await eventsub.listen_channel_points_custom_reward_redemption_add(user.id, on_message_read_reward,
                                                                      "384087a0-a0e4-4090-a8a9-75c04da6f0b5")

    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_ready)

    chat.set_prefix("!")
    #chat.register_command("discord", discord_invitation)

    chat.start()

    await asyncio.Event().wait()

asyncio.run(init_twitch())