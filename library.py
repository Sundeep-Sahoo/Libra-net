from datetime import datetime, timedelta
import re

# ---------------- Custom Exception ----------------
class LibraryException(Exception):
    pass


# ---------------- Base Item ----------------
class Item:
    def __init__(self, item_id: int, title: str, author: str):
        self.id = item_id
        self.title = title
        self.author = author
        self.available = True

    def get_type(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.get_type()}(ID={self.id}, Title='{self.title}', Author='{self.author}', Available={self.available})"


class Book(Item):
    def __init__(self, item_id: int, title: str, author: str, page_count: int):
        super().__init__(item_id, title, author)
        self.page_count = page_count

    def get_type(self):
        return "Book"


class Playable:
    def play(self):
        raise NotImplementedError()


class AudioBook(Item, Playable):
    def __init__(self, item_id: int, title: str, author: str, playback_minutes: int):
        super().__init__(item_id, title, author)
        self.playback_minutes = playback_minutes

    def play(self):
        print(f"Playing audiobook: {self.title}")

    def get_type(self):
        return "AudioBook"


class EMagazine(Item):
    def __init__(self, item_id: int, title: str, author: str, issue_number: int):
        super().__init__(item_id, title, author)
        self.issue_number = issue_number
        self.archived = False

    def archive_issue(self):
        self.archived = True
        print(f"Issue {self.issue_number} of {self.title} archived.")

    def get_type(self):
        return "EMagazine"


class BorrowRecord:
    def __init__(self, item_id: int, borrower_id: int, borrow_date: datetime, expected_return_date: datetime):
        self.item_id = item_id
        self.borrower_id = borrower_id
        self.borrow_date = borrow_date
        self.expected_return_date = expected_return_date
        self.actual_return_date = None


class Library:
    def __init__(self, fine_per_day=10.0):
        self.items = {}
        self.active_borrows = {}
        self.fines_by_user = {}
        self.fine_per_day = fine_per_day

    def add_item(self, item: Item):
        if item.id in self.items:
            raise LibraryException("Item with this ID already exists")
        self.items[item.id] = item

    def borrow_item(self, item_id: int, borrower_id: int, duration_str: str):
        if item_id not in self.items:
            raise LibraryException("Item not found")
        item = self.items[item_id]
        if not item.available:
            raise LibraryException("Item already borrowed")

        days = self.parse_duration_to_days(duration_str)
        borrow_date = datetime.now()
        expected_return = borrow_date + timedelta(days=days)
        record = BorrowRecord(item_id, borrower_id, borrow_date, expected_return)

        item.available = False
        self.active_borrows[item_id] = record
        print(f"Borrowed {item} for {days} days by user {borrower_id}")

    def return_item(self, item_id: int):
        if item_id not in self.active_borrows:
            raise LibraryException("Item was not borrowed")

        record = self.active_borrows.pop(item_id)
        return_date = datetime.now()
        record.actual_return_date = return_date

        allowed_days = (record.expected_return_date - record.borrow_date).days
        actual_days = (return_date - record.borrow_date).days
        overdue = max(0, actual_days - allowed_days)
        fine = overdue * self.fine_per_day

        if fine > 0:
            self.fines_by_user[record.borrower_id] = self.fines_by_user.get(record.borrower_id, 0) + fine
            print(f"Returned late by {overdue} days. Fine: {fine}")
        else:
            print(f"Returned on time.")

        self.items[item_id].available = True

    def search_by_type(self, type_name: str):
        return [item for item in self.items.values() if item.get_type().lower() == type_name.lower()]

    def search_by_title(self, keyword: str):
        return [item for item in self.items.values() if keyword.lower() in item.title.lower()]

    def parse_duration_to_days(self, s: str) -> int:
        pattern = r"^(\d+)\s*(d|day|days|h|hr|hrs|hour|hours|w|week|weeks)?$"
        match = re.match(pattern, s.strip().lower())
        if not match:
            raise LibraryException("Invalid duration format")

        value = int(match.group(1))
        unit = match.group(2)

        if unit is None or unit.startswith("d"):
            return max(1, value)
        elif unit.startswith("h"):
            return max(1, (value + 23) // 24)
        elif unit.startswith("w"):
            return max(1, value * 7)
        return value
