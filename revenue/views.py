from django.db import connection
from django.shortcuts import render

# Create your views here.


def Revenue( request ):
    
    query = """
        SELECT school_title AS sch
	    FROM school_t;
    """
    with connection.cursor() as cursor:
        cursor.execute( query )
        schools = [ row[0] for row in cursor.fetchall() ]

    sqlClause = ""
    for school in schools:
        sqlClause += f"SUM( CASE WHEN E.School = '{school}' THEN Revenue ELSE 0 END ) AS {school},\n"



    query = f"""
SELECT SUM( Revenue ) AS Total,
            ROUND( 
                100 * ( 
                     SUM( Revenue ) - LAG( SUM( Revenue ), 3,  SUM( Revenue ) ) OVER () 
                ) / SUM( Revenue ) 
            ) AS '% Change'
        FROM (
            SELECT 
                syear AS Years, 
                session_name AS Sessions, 
                SUM( S.enroll_capacity * C.credit_hours ) AS Revenue, 
                D.school_title AS School
            FROM 
                section_t S, 
                coofferedwith_t O, 
                course_t C,
                department_t D, 
                (
                    SELECT syear AS Years, session_name AS Sessions
                    FROM Section_T
                    GROUP BY syear, session_name
                ) M
            WHERE 
                    S.course_id = O.course_id
                AND O.course_id = C.course_id 
                AND S.dept_id = D.dept_id
                AND S.syear = M.Years
                AND S.session_name = M.Sessions
            GROUP BY Years, Sessions, School
            ORDER BY Years, Sessions
        ) E
        GROUP BY Years, Sessions
        ORDER BY Years, Sessions DESC
    """
    with connection.cursor() as cursor:
        cursor.execute( query )
        labels = [ col[0] for col in cursor.description ]
        data = cursor.fetchall()

    # xAxis, yAxis, totals, changes =RevenueChartDataPacker( data, labels )

    return render( request, "revenue/revenue_iub.html", { 
            'colNames': labels,
            'revenues': data,
            # 'xAxis': xAxis,
            # 'yAxis': yAxis ,
            # 'totals': totals,
            # 'changes': changes 
        }
    )