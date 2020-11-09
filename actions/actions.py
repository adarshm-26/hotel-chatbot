from dateutil import parser
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
    
    validated_number = None

    # Slot value should always be a number
    if isinstance(slot_value, int):
      validated_number = slot_value
    elif isinstance(slot_value, Text) and slot_value.isdigit():
      validated_number = int(slot_value)

    return { 'number': validated_number }

  def validate_type(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    
    validated_type = None

    # Slot value should always be one of existing room types
    if isinstance(slot_value, Text) and slot_value.lower() in self.room_types():
      validated_type = slot_value.title()
    elif isinstance(slot_value, List):
      for room_type in slot_value:
        if isinstance(room_type, Text) and room_type.lower() in self.room_types():
          validated_type = room_type.title()
          break

    return { 'type': validated_type }

  def validate_from_date(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    
    temp_date = ''
    validated_date = None

    if isinstance(slot_value, Text):
      temp_date = slot_value
    # Sometimes Duckling extracts a Dict to convey range information
    elif isinstance(slot_value, Dict):
      # 'from' seems sensible to extract first here
      if 'from' in slot_value and slot_value['from'] is not None:
        temp_date = slot_value['from']
      # take the 'to' value if 'from' is absent
      elif 'to' in slot_value and slot_value['to'] is not None:
        temp_date = slot_value['to']

    if temp_date:
      validated_date = temp_date.split('T')[0]
    return { 'from_date': validated_date }
  
  def validate_to_date(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    
    temp_date = ''
    validated_date = None

    if isinstance(slot_value, Text):
      temp_date = slot_value
    # Sometimes Duckling extracts a Dict to convey range information
    elif isinstance(slot_value, Dict):
      # 'to' seems sensible to extract first here
      if 'to' in slot_value and slot_value['to'] is not None:
        temp_date = slot_value['to']
      # take the 'to' value if 'from' is absent
      elif 'from' in slot_value and slot_value['from'] is not None:
        temp_date = slot_value['from']

    if temp_date:
      validated_date = temp_date.split('T')[0]
    return { 'to_date': validated_date }
      
class ValidateCleaningForm(FormValidationAction):

  def name(self) -> Text:
    return 'validate_cleaning_form'

  def validate_cleaning_time(
    self,
    slot_value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:

    temp_time = ''
    validated_time = None

    if isinstance(slot_value, Text):
      temp_time = slot_value
    elif isinstance(slot_value, Dict):
      # check both 'to' and 'from' as Duckling may 
      # extract any
      if 'to' in slot_value and slot_value['to'] is not None:
        temp_time = slot_value['to']
      elif 'from' in slot_value and slot_value['from'] is not None:
        temp_time = slot_value['from']
    
    if temp_time:
      validated_time = ' '.join(temp_time.split('T'))
    return { 'cleaning_time': validated_time }
      