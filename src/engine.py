from datetime import date
import calendar 
from typing import List
from src.models import Shift, Staff
from src.io_handler import load_staff_from_excel
from ortools.sat.python import cp_model
import streamlit as st

def assign_staff_to_shifts(staff_list, shifts):
    model = cp_model.CpModel()

    assignments = {}

    for s_idx, s in enumerate(shifts):
        for staff in staff_list:
            varName = f"s{s_idx}_{staff.name}"
            assignments[(staff.name, s_idx)] = model.NewBoolVar(varName)

    # Hard Constraint: Each shift must hvae 1 staff assigned to it 
    for s_idx, s in enumerate(shifts):
        model.Add(sum(assignments[(staff.name, s_idx)]) == 1 for staff in staff_list)


    # Hard Constraint: Exclude staff from shifts on unavailable dates
    for s_idx, s in enumerate(shifts):
        for staff in staff_list:
            if s.shiftDate in staff.unavailDates:
                model.Add(assignments[(staff.name, s_idx)] == 0)

    # Hard Constraint: Assign shifts to staff who bidded for it
    bidders = []
    for s_idx, s in enumerate(shifts):
        bidders = [staff for staff in staff_list if s.shiftDate in staff.biddingDates]
        if bidders: # if there are bidders for the shift
            model.Add(sum(assignments[(bidder.name, s_idx)]) == 1 for bidder in bidders)

    # Soft Constraint: Fairness
    # since 1 point represent 1 shift
    total_staff_points = {}
    for staff in staff_list:
        initialPoints = staff.points 
        pointsGained = sum(assignments[(staff.name, s_idx)] for s_idx, s in shifts) # points gained after completing all the shifts scheduled for staff
        total_points_var = model.NewIntVar(0, 10000, "total_p") 
        model.Add(total_points_var == initialPoints + pointsGained)
        total_staff_points[staff.name] = total_points_var
        
    highest = model.NewIntVar(0, 10000, "highest_p")
    lowest = model.NewIntVar(0, 10000, "lowest_p")

    for points in total_staff_points.values():
        model.Add(highest >= points)
        model.Add(lowest <= points)

    model.Minimize(highest-lowest)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        results = []
        for s_idx, s in enumerate(shifts):
            for staff in staff_list:
                if solver.Value(assignments[(staff.name, s_idx)]) == 1:
                    staff.points += s.shiftPoints 
                    s.assignedStaff = staff
                    results.append({"Name":staff.name, "Points":staff.points, "Shift Date":s.shiftDate})
        return results
    return None