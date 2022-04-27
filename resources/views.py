from django.shortcuts import render
from django.db import connection


# Create your views here.
'''
Comparative analysis of percentage of unused resources for each school in selected
semester/s, as well as w.r.t to total unused percentage for the university overall based on
average enrollment per section versus average capacity per room.
'''
def unusedresources(request):

#to get session names 
    query =   """     
            SELECT session_name      
            FROM section_t
            GROUP BY session_name
            """
    sessions = [] #creating a dictionary containing all session names
    with connection.cursor() as cursor:
        cursor.execute(query)
        sessions = cursor.fetchall() #fetches all the rows of the query above and stores them as tuples
   # return render(request, 'Percentage_of_unused_resources.html')

   
    yquery = """     
            SELECT syear
            FROM section_t
            GROUP BY syear
            ORDER BY syear
            """
    years = []
    with connection.cursor() as cursor:
        cursor.execute(yquery)
        years = cursor.fetchall()

    year=''
    session= ''    
#use custom code to get selected year and session which counts for specific semester
    if request.method == 'POST':
        year = request.POST.get('selected_year', "2020")
        session = request.POST.get('selected_session', "Autumn")

    else:
        year = years[-1][0]
        session = sessions[-1][0]
       
#rounded the values, grouped by school title as the query asks for each school's  info
     
    rquery =  """
            SELECT School_Title AS School_Title,
             Enroll_Avg AS Enroll_Avg, Avg_Capacity_Room AS Avg_Capacity_Room, unused AS Unused_Resources_Percentage

            FROM (
                SELECT 
                    d.school_title AS School_Title,
                    ROUND(AVG( s.enroll_capacity),3) AS Enroll_Avg, 
                    ROUND(AVG( c.room_capacity ),3) AS Avg_Capacity_Room,
                    ( AVG(c.room_capacity) - AVG( s.enroll_capacity )) AS value,
                    ROUND((value/Avg_Capacity_Room)*100, 3) AS unused
                    
                FROM department_t AS d, section_t as s, classroom_t c
                WHERE
               	   d.dept_id = s.dept_id
               	   AND s.room_id= c.room_id 
                   AND s.session = %(session)s
                   AND s.syear = %(year)s 
                   GROUP BY d.school_title 
                ) AS DATA
            """
      
    val={
        "year" : str(year),
        "session" : session,
    }
    with connection.cursor() as cursor:
        cursor.execute( rquery , val)
        # print(connection.queries)
        tableHeaders = [ col[0] for col in cursor.description ]
        tableData = cursor.fetchall()
    context = {
        'tableHeaders' : tableHeaders,
        'tableData'    : tableData,
        'years'        : years,
        'sessions'     : sessions,
        'selected_session' : session,
        'selected_year'    : year,
        
    }
    return render(request,'Percentage_of_unused_resources.html')
