from dateutil import parser
from typing import Text, List, Any, Dict
from pymongo import MongoClient
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.interfaces import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import ActionExecuted

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
    # Sometimes Duckling extracts a Dict 
    # to convey range information
    elif isinstance(slot_value, Dict):
      # 'from' seems sensible to extract first here
      if 'from' in slot_value and slot_value['from'] is not None:
        temp_date = slot_value['from']
      # take the 'to' value if 'from' is absent
      elif 'to' in slot_value and slot_value['to'] is not None:
        temp_date = slot_value['to']

    if temp_date:
      validated_date = convert_to_readable(temp_date)
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
    # Sometimes Duckling extracts a Dict 
    # to convey range information
    elif isinstance(slot_value, Dict):
      # 'to' seems sensible to extract first here
      if 'to' in slot_value and slot_value['to'] is not None:
        temp_date = slot_value['to']
      # take the 'to' value if 'from' is absent
      elif 'from' in slot_value and slot_value['from'] is not None:
        temp_date = slot_value['from']

    if temp_date:
      validated_date = convert_to_readable(temp_date)
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
      validated_time = convert_to_readable(temp_time, True)
    return { 'cleaning_time': validated_time }

def convert_to_readable(date, parse_time = False):
  """Utility function to convert dates 
  to easily understandable form"""

  days_of_week = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
  ]

  month_short_names = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ]

  parsed_date = parser.parse(date).astimezone()
  day_of_week = days_of_week[parsed_date.weekday()]
  month_name = month_short_names[parsed_date.month-1]
  
  readable_datetime = "{} {}th {}{}"
  time_part = ''
  if parse_time:
    parsed_time = parsed_date.time()
    time_part += " at {}".format(parsed_time.hour % 12)
    if parsed_time.minute % 15 is 0:
      time_part += ":{:02}".format(parsed_time.minute)
    time_part += 'PM' if parsed_time.hour >= 12 else 'AM'

  return readable_datetime.format(day_of_week, parsed_date.day, month_name, time_part)

class ActionSaveForm(Action):

  MAX_TURNS_TO_SEARCH = 50

  def name(self) -> Text:
    return 'action_save_form'

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> List[Any]:

    client = MongoClient('mongodb://localhost:27017/')
    db = client['hotel-chatbot']

    coll_name = ''
    document_data = {}

    for turn, event in enumerate(reversed(tracker.events)):
      name = event.get('name')
      # Check only for the latest form
      if name == 'booking_form':
        coll_name = 'bookings'
        document_data.update(tracker.slots)
        del document_data['cleaning_time']
        break
      elif name == 'cleaning_form':
        coll_name = 'cleanings'
        document_data.update({
          'cleaning_time': tracker.get_slot('cleaning_time')
        })
        break
      # To prevent being stuck in a loop
      if turn >= self.MAX_TURNS_TO_SEARCH:
        break

    # Insert into DB only if recent and valid form was found
    if coll_name:
      db[coll_name].insert_one(document_data)

    return []
