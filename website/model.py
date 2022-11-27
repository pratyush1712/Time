from ortools.linear_solver import pywraplp
import datetime
from . import db
from .models import Assignment, Timeslot
from math import ceil
from random import randint


def runAssign(assignments, timeslots, user):
    INITIAL_COST = 20
    PREFERED_TIME_DECREMENT = 5
    PRIORITY_DECREMENT = int(1/9*INITIAL_COST)
    
    # data
    num_assignments = len(assignments)+1
    num_slots = len(timeslots)
    all_slots = range(num_slots)
    all_assignments = range(len(assignments))
    
    # cost table
    costs = []
    for a in range(len(assignments)):
        lis = []
        for s in all_slots:
            cost = INITIAL_COST
            if timeslots[s].get("startTime").time()>=datetime.time(hour=18, minute=0):
                if user.preferedWorkTime == 1:
                    cost = (INITIAL_COST-PREFERED_TIME_DECREMENT)
            if timeslots[s].get("startTime").time()<datetime.time(hour=18, minute=0):
                if user.preferedWorkTime == 0:
                    cost = (INITIAL_COST-PREFERED_TIME_DECREMENT)
            cost-=PRIORITY_DECREMENT*assignments[a].get("priority")
            lis.append(cost)
        costs.append(lis)
    # assign costs
    count=0
    for aID in all_assignments:
        for sID in all_slots:
            #print(timeslots[sID]["endTime"] > assignments[aID]["duedate"])
            count+=1
            if timeslots[sID]["endTime"] > assignments[aID]["duedate"]:
                costs[aID][sID] = 50000000
    
    # Create the mip solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    # create the variables
    x = {}
    for aID in range(1,(num_assignments)+1):
        for sID in range(1,(num_slots)+1):
            x[aID,sID] = solver.IntVar(0,1,'')
    
    # constraints
    # 1. Every slot is alloted to at most one assignment
    for sID in range(1,(num_slots)+1):
        solver.Add(solver.Sum([x[aID, sID] for aID in range(1,(num_assignments)+1)]) == 1)
    
    # 2. The number of slots alloted to an assignment is greater than the demand
    for aID in range(1,(len(assignments))+1):
        time = assignments[aID-1]["amtOfTime"].seconds//60
        solver.Add(solver.Sum([x[aID, sID]*((timeslots[sID-1]["endTime"]-timeslots[sID-1]["startTime"]).seconds//60) for sID in range(1,(num_slots)+1)]) >= time)
        solver.Add(solver.Sum([x[aID, sID]*((timeslots[sID-1]["endTime"]-timeslots[sID-1]["startTime"]).seconds//60) for sID in range(1,(num_slots)+1)]) <= (user.maxFocusTime*60+time))
    
    # objective function
    obj = []
    for aID in range(len(assignments)):
        for sID in all_slots:
            obj.append(costs[aID][sID]*x[aID+1,sID+1])
    solver.Minimize(solver.Sum(obj))

    # invoke the solver
    status = solver.Solve()
    # update the db
    if status == pywraplp.Solver.OPTIMAL:
        for aID in range(1,(num_assignments)):
            for sID in range(1,(num_slots)):
                if x[aID,sID].solution_value() == 1:
                    print(aID,sID)
                    slot = Timeslot.query.filter_by(id=timeslots[sID-1].get("id")).first()
                    slot.assignment = assignments[aID-1].get("id")
                    db.session.commit()

def runTest(assignments, timeslots):
    """
    Testing v1...
    
    Types:
    assignments = list of dictionaries of the form:
    {
        "id": xyz,
        "name": xyz,
        "duedate": {a datetime object},
        "amtOfTime": {amt of time the user expects to spend on this thing},
        "timeslots": [a list of all the timeslots assigned to this assignment (currently empty)]
    }
    timeslots = list of dictionaries of the form:
    {
        "id": xyz,
        "startTime": {a datetime object},
        "endTime": {a datetime object 25 minutes ahead of the startTime},
        "assignment": {the id of the assignment that is assigned to this slot (currently None)}
    }
    """
    # data
    num_assignments = len(assignments)
    num_timeslots = len(timeslots)
    all_slots = range(num_timeslots)
    all_assignments = range(num_assignments)
    
    # create the model
    solver = pywraplp.Solver.CreateSolver('SCIP')
    assign = {}
    
    # create variables
    for a in all_assignments:
        for s in all_slots:
            assign[(a,s)] = solver.IntVar(0.0, 1, f"{a},{s}")
    
    # constraints that says every slot is assigned to at most one assignment
    for s in all_slots:
        solver.Add(sum(assign[(a,s)] for a in all_assignments) == 1)
    
    # constraint that says [the number of slots alloted to an assignment]*25 >= expected_time
    for a in all_assignments:
        time=0
        for s in all_slots:
            print(assign[(a,s)])
        # ext = sum(assign[(a,s)] for s in all_slots)
        # print(ext)
        print("                                                                                                                                                                                                                                                                                        ")
        solver.Add(datetime.timedelta(minutes=sum(assign[(a,s)] for s in all_slots)*25) >= assignments[a].get("amtOfTime"))
    
    # constraint that says the endTime of the last timeslot alloted to an assignment is before assignment's deadline
    for a in all_assignments:
        acceptable = []
        for s in all_slots:
            if timeslots[s].get("endTime") <= assignments[a].get("duedate"):
                acceptable.append(s)
        for s in all_slots:
            if s not in acceptable:
                solver.Add(assign[(a,s)] == 0)
    
    # objective function: minimize the time spent on each assignment
    minima = 0
    for a in all_assignments:
        for s in all_slots:
            minima+=assign[(a,s)]
    solver.Minimize(minima)
    
    # call the solver
    status = solver.Solve()
    
    # update the database
    for a in all_assignments:
        for s in all_slots:
            if assign[(a,s)] == 1:
                slot = Timeslot.query.filter_by(id=s).first()
                slot.assignment = a
                db.session.commit()
