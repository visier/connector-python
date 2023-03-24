SELECT 
    employeeCount(),
    level(Location, "Location_0"),
    level(Gender, "Gender"),
    level(Union_Status, "Union_Status"),
    level(Location, "Location_1")
FROM Employee 
WHERE 
    Visier_Time IN periods(date("2020-04-01"), 2, period(3, Month))