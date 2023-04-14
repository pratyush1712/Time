# Time Bite
- Automate planning. It takes your tasks and projects. And builds the perfect daily schedule.

## Overview
- The application automates time management and schedule making for the user based on their prefered work habits.
- It asks user for their prefered study/work time and the number of hours they can spend working without losing focus.
- The user can then create their Todo list specfying the number of hours they expect to spend on each task, the duedate for each task, and the importance of every task on a scale of 1-10.
- The application runs Simplex Algorithm to build an optimized scchedule for the user in which appropriate amount of breaks are involved, and each task in done before its deadline.
- Then, the application sends the schedule to user's Google Calendar.
## Code Overview
- Built the backend (SQL Database) using Flask, and SQL-Alchemy.
- Used Google OR tools to make an Integer Linear Program model to optimize the user's schedule.
- Integrated Google Calendar API to export the schedule created to user's Google Calendar.
- Built the frontend using HTML, CSS, JavaScript.
- Added authentication in the flask-backend.
## Features to be added
- Cross-platform application (Flutter): The front end of the application is being developed using Flutter.
- Shared projects: The application enables the user to add members for group assignments. App would sync and create schedules for each members.
- Close friends: The application enables the user to add their friends in their close friends list so that they can find shared free space in their calendar in which they can hangout.

website link: https://timebite.herokuapp.com/
