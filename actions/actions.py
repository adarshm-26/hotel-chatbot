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
    if isinstance(slot_value, int):
      return { 'number': slot_value }
    elif isinstance(slot_value, Text) and slot_value.isdigit():
      return { 'number': int(slot_value) }
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
    if isinstance(slot_value, Text) and slot_value.lower() in self.room_types():
      return { 'type': slot_value.lower() }
    elif isinstance(slot_value, List):
      for room_type in slot_value:
        if isinstance(room_type, Text) and room_type.lower() in self.room_types():
          return { 'type': room_type.lower() }
      return { 'type': None }
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
      return { 'from_date': slot_value.split('T')[0] }
    # Sometimes Duckling extracts a Dict to convey range information
    # 'from' seems sensible to extract here
    elif isinstance(slot_value, Dict) and 'from' in slot_value:
      if slot_value['from'] is not None:
        return { 'from_date': slot_value['from'].split('T')[0] }
      else:
        return { 'from_date': None }
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
      return { 'to_date': slot_value.split('T')[0] }
    # Sometimes Duckling extracts a Dict to convey range information
    # 'to' seems sensible to extract here
    elif isinstance(slot_value, Dict) and 'to' in slot_value:
      if slot_value['to'] is not None:
        return { 'to_date': slot_value['to'].split('T')[0] }
      else:
        return { 'to_date': None }
    else:
      return { 'to_date': None }
      