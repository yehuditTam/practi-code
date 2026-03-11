from io_comp.csv_reader import read_calendar_csv
from io_comp.scheduler import find_available_slots
from datetime import timedelta, time

events = read_calendar_csv('resources/calendar.csv')
slots = find_available_slots(['Alice', 'Jack'], timedelta(hours=1), events)

print("Expected from exercise:")
print("07:00")
print("09:40 - 12:00")
print("14:00 - 15:00")
print("17:00 - 18:00")
print()

print("Our results - Key times:")
key_times = [time(7,0), time(9,40), time(12,0), time(14,0), time(15,0), time(17,0), time(18,0)]
for t in key_times:
    status = 'YES' if t in slots else 'NO'
    print(f'{t.strftime("%H:%M")}: {status}')

print()
print("Summary:")
print(f"Total slots found: {len(slots)}")
print(f"First slot: {slots[0].strftime('%H:%M')}")
print(f"Last slot: {slots[-1].strftime('%H:%M')}")
