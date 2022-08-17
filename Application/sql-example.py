# you may need to install dnspython and protobuf 3.6.1 in pip to make this work! for some reason these did not come
# default with my installation of the connector
import mysql.connector

cnx = mysql.connector.connect(user='admin', password='uuhg7K1I2Ep8gL9k0ddG',
                              host='co600-2.cmgp3lpwnvuv.us-east-2.rds.amazonaws.com',
                              database='university-review')

cursor = cnx.cursor()

# Pages are all identified by a page ID. Non uni pages are also identified by a parent ID, which is the ID of a uni page

query = "SET @uniID := (SELECT pageID FROM Page WHERE pageName = %s);"  # Gets the ID of a university given a name
cursor.execute(query, ("University of Kent",)) # Executes finding ID, given name "University of Kent"
cursor.execute("SELECT * FROM Page WHERE pageID = @uniID OR pageParent = @uniID") # Gets all data for page and parents

rows = cursor.fetchall() # Produces list of tuples - "rows" is the var in which the data is being stored 
print(rows)

cursor.close()
cnx.close()

# Expected sample output:
# [(1, None, 'University of Kent', 'University', 'Lorem ipsum'), (2, 1, 'Kent Sport', 'Facilities', 'Lorem ipsum')], etc
# Columns are, as of writing, ID, parent ID, name, type, description
