import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mypassword",
  database = "ignite"
)
mycursor = mydb.cursor()

mycursor.execute("""CREATE TABLE `recommender` (
                    `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
                    `MEMBER_ID` varchar(255) NOT NULL,
                    `TIMES` int(11) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""")

mycursor.execute("""CREATE TABLE `voting_score` (
                    `ID` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
                    `MEMBER_ID` varchar(255) NOT NULL,
                    `RECOMMENDER` int(11) NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """)

mycursor.execute(""" ALTER TABLE `voting_score`
                    ADD CONSTRAINT `recommend_id` FOREIGN KEY (`RECOMMENDER`) REFERENCES `recommender` (`ID`); """)