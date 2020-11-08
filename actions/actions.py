# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import datetime
from typing import Text, List, Any, Dict
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ValidateBookingForm(FormValidationAction):

  def name(self) -> Text:
    return 'validate_booking_form'

  @staticmethod
  def room_types() -> List[Text]:
    return ['simple', 'deluxe', 'suite']

  def validate_number(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    # Slot value should always be a number
    raise TypeError('Reached number validation')
    if slot_value.isdigit():
      return { 'number': slot_value }
    else:
      return { 'number': None }

  def validate_type(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    # Slot value should always be one of existing room types
    if slot_value.lower() in self.room_types():
      return { 'type': slot_value }
    else:
      return { 'type': None }

  def validate_from_date(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    if isinstance(slot_value, Text):
      return { 'from_date': slot_value }
    # Sometimes Duckling extracts a Dict to convey range information
    # 'from' seems sensible to extract here
    elif isinstance(slot_value, Dict) and 'from' in slot_value:
      return { 'from_date': slot_value['from'] }
    else:
      return { 'from_date': None }
  
  def validate_to_date(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    if isinstance(slot_value, Text):
      return { 'to_date': slot_value }
    # Sometimes Duckling extracts a Dict to convey range information
    # 'to' seems sensible to extract here
    elif isinstance(slot_value, Dict) and 'to' in slot_value:
      return { 'to_date': slot_value['to'] }
    else:
      return { 'to_date': None }
      