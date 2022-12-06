class Lesson:
    def __init__(self, booking, date_time, student_name="defaultname", 
                teacher="defaultteacher", duration="30 mins", 
                further_info="defaultfurtherinfo"):
        self.booking = booking
        self.date_time = date_time
        self.student_name = student_name
        self.teacher = teacher
        self.duration = duration
        self.further_info = further_info

    def __eq__(self, other) : 
        return self.__dict__ == other.__dict__