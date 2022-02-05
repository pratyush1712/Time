from ortools.linear_solver import pywraplp
import datetime
from math import ceil
from random import randint


sample_database = {
    "assignments": [{
        "id": 1,
        "name": "xxx",
        "duedate": datetime.datetime(month=12,year=2021,day=17,hour=23,minute=59),
        "amtOfTime": datetime.timedelta(minutes=50),
        "timeslots": []
    },
    {
        "id": 2,
        "name": "yyy",
        "duedate": datetime.datetime(month=12,year=2021,day=17,hour=21,minute=59),
        "amtOfTime": datetime.timedelta(minutes=50),
        "timeslots": []
    },
    {
        "id": 3,
        "name": "zzz",
        "duedate": datetime.datetime(month=12,year=2021,day=17,hour=17,minute=59),
        "amtOfTime": datetime.timedelta(minutes=45),
        "timeslots": []
    }],
    "timeslots": [
    {
        "id": 1,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=11,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=12,minute=10),
        "day": 5
    },
    {
        "id": 2,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=12,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=12,minute=40),
        "day": 5
    },
    {
        "id": 3,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=12,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=13,minute=10),
        "day": 5
    },
    {
        "id": 4,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=13,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=13,minute=40),
        "day": 5
    },
    {
        "id": 5,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=14,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=14,minute=40),
        "day": 5
    },
    {
        "id": 6,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=14,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=15,minute=10),
        "day": 5
    },
    {
        "id": 7,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=15,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=15,minute=40),
        "day": 5
    },
    {
        "id": 8,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=15,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=16,minute=10),
        "day": 5
    },
    {
        "id": 9,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=16,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=17,minute=10),
        "day": 5
    },
    {
        "id": 10,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=17,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=17,minute=40),
        "day": 5
    },
    {
        "id": 11,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=17,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=18,minute=10),
        "day": 5
    },
    {
        "id": 12,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=18,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=18,minute=40),
        "day": 5
    },
    {
        "id": 13,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=18,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=19,minute=10),
        "day": 5
    },
    {
        "id": 14,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=19,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=19,minute=40),
        "day": 5
    },
    {
        "id": 15,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=20,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=20,minute=40),
        "day": 5
    },
    {
        "id": 16,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=20,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=21,minute=10),
        "day": 5
    },
    {
        "id": 17,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=21,minute=15),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=21,minute=40),
        "day": 5
    },
    {
        "id": 18,
        "assignment": None,
        "startTime": datetime.datetime(month=12,year=2021,day=17,hour=21,minute=45),
        "endTime": datetime.datetime(month=12,year=2021,day=17,hour=22,minute=10),
        "day": 5
    }
]
}


def runAssign(assignments, timeslots):
    # data
    num_assignments = len(assignments)
    num_slots = len(timeslots)
    all_slots = range(num_slots)
    all_assignments = range(num_assignments)
    
    # cost table
    costs = []
    for a in all_assignments:
        lis = []
        for s in all_slots:
            lis.append(randint(1,num_assignments))
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
    for aID in all_assignments:
        for sID in all_slots:
            x[aID,sID] = solver.IntVar(0,1,'')
    
    # constraints
    # 1. Every slot is alloted to at most one assignment
    for sID in all_slots:
        solver.Add(solver.Sum([x[aID, sID] for aID in all_assignments]) == 1)
    
    # 2. The number of slots alloted to an assignment is greater than the demand
    for aID in all_assignments:
        time = assignments[aID]["amtOfTime"].seconds//60
        slotsReq = ceil(time/25)
        solver.Add(solver.Sum([x[aID, sID] for sID in all_slots]) >= slotsReq)
    
    # objective function
    obj = []
    for aID in all_assignments:
        for sID in all_slots:
            obj.append(costs[aID][sID]*x[aID,sID])
    solver.Minimize(solver.Sum(obj))

    # invoke the solver
    status = solver.Solve()

    # update the db
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        for aID in all_assignments:
            for sID in all_slots:
                if x[aID, sID].solution_value() == 1:
                    timeslots[sID]["assignment"] = aID
                    assignments[aID]["timeslots"].append(sID)

    

def run(assignments, timeslots):
    """
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
        "endTime": {a datetime object 25 minute ahead of the startTime},
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
    for aID in all_assignments:
        time = assignments[aID]["amtOfTime"].seconds//60
        slotsReq = ceil(time/25)
        solver.Add(solver.Sum([assign[(aID, sID)] for sID in all_slots]) >= slotsReq)
    
    # constraint that says the endTime of the last timeslot alloted to an assignment is before assignment's deadline
    for a in all_assignments:
        for s in all_slots:
            if timeslots[s].get("endTime") > assignments[a].get("duedate"):
                solver.Add(assign[(a,s)] == 0)
        
    # objective function: minimize the time spent on each assignment
    minima = 0
    for a in all_assignments:
        for s in all_slots:
            minima+=assign[(a,s)]
    solver.Maximize(minima)
    
    # call the solver
    status = solver.Solve()
    
    # update the database
    for a in all_assignments:
        for s in all_slots:
            if assign[(a,s)] == 1:
                timeslots[s]["assignment"] = a
                assignments[a]["timeslots"].append(s)
    

    # additional constraint for nurse solver
        # the sum of all timeslots for an assignment has to be greater that the amount of time expected to complete that assignment
        # the endTime of the last timeslots alloted to an assignment has to be before the duedate of the assignment

if __name__ == "__main__":
    # run the LP on the sample database
    runAssign(sample_database.get("assignments"), sample_database.get("timeslots"))
    for slot in sample_database.get('assignments'):
        print(slot)
        print('\n')