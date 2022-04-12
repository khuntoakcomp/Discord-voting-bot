from discord.ext import commands
import discord
import mysql.connector
from collections import Counter

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="mypassword",
  database = "ignite"
)
mycursor = mydb.cursor()

TOKEN = "Your token" 
client = commands.Bot(command_prefix='$') #ex. $checkscore you can change it

@client.event
async def on_ready():
    print("Bot is ready")

@client.command()
async def checkscore(ctx,user: discord.User):
    sql = "SELECT * FROM voting_score WHERE MEMBER_ID = %s"
    id = (user.id,)
    mycursor.execute(sql, id)
    all_vote = mycursor.fetchall()
    total = len(all_vote)
    await ctx.send("Total voting score of {} is {}".format(user,total))

@client.command()
async def ranking(ctx):
    sql = "SELECT MEMBER_ID, COUNT(MEMBER_ID) AS num FROM voting_score GROUP BY MEMBER_ID having num > 0 order by count(MEMBER_ID) desc limit 5"
    mycursor.execute(sql)
    all_vote = mycursor.fetchall()
    firstrank = 'user id : {} got voted {} times'.format(all_vote[0][0],all_vote[0][1])
    secondrank = 'user id : {} got voted {} times'.format(all_vote[1][0],all_vote[1][1])
    thirdrank = 'user id : {} got voted {} times'.format(all_vote[2][0],all_vote[2][1])
    embed = discord.Embed(title='Top voted score', description='Top 3 user id who got most voted', color=0xff5555)
    embed.add_field(name='**1st Place**', value=firstrank, inline=False)
    embed.add_field(name='**2nd Place**', value=secondrank, inline=False)
    embed.add_field(name='**3rd Place**', value=thirdrank, inline=False)
    await ctx.send(embed=embed)

@client.command()
@commands.has_role("admin")  #your role name
async def offer(ctx, user: discord.User):
    sql = "SELECT TIMES FROM recommender WHERE MEMBER_ID = %s"
    recommender = (ctx.message.author.id,)
    mycursor.execute(sql, recommender)
    max_times = mycursor.fetchone()
    if ctx.message.author.id != user.id:
        if max_times != None and max_times[0] < 3:  # maximun time that user can vote
            query_rec = "SELECT ID FROM recommender WHERE MEMBER_ID = %s"
            mycursor.execute(query_rec, recommender)
            recommender_id = mycursor.fetchone()
            if recommender_id != None:
                query_user = "SELECT MEMBER_ID,RECOMMENDER FROM voting_score WHERE MEMBER_ID = %s"
                user_id = (user.id,)
                mycursor.execute(query_user, user_id)
                all_vote = mycursor.fetchall()
                check_dup = [ele for ele, count in Counter(all_vote).items() if count > 0]
                if check_dup == []:
                    sql = "INSERT INTO voting_score (MEMBER_ID,RECOMMENDER) VALUES (%s,%s)"
                    val = (user.id,recommender_id[0])
                    mycursor.execute(sql, val)
                    mydb.commit()
                    sql = "UPDATE recommender SET TIMES = %s WHERE MEMBER_ID = %s "
                    times = max_times[0] + 1
                    val = (times,ctx.message.author.id)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    await ctx.send('voting_complete')
                else:
                    await ctx.send('cannot vote same person')
            else:
                await ctx.send('Error No recommender')
        elif max_times == None:
            sql = "INSERT INTO recommender (MEMBER_ID,TIMES) VALUES (%s,%s)"
            val = (ctx.message.author.id,1)
            mycursor.execute(sql, val)
            mydb.commit()
            query_rec = "SELECT ID FROM recommender WHERE MEMBER_ID = %s"
            mycursor.execute(query_rec, recommender)
            recommender_id = mycursor.fetchone()
            if recommender_id != None:
                sql = "INSERT INTO voting_score (MEMBER_ID,RECOMMENDER) VALUES (%s,%s)"
                val = (user.id,recommender_id[0])
                mycursor.execute(sql, val)
                mydb.commit()
                await ctx.send('voting_complete')
            else:
                await ctx.send('Error No recommender')
        else:
            await ctx.send('your quota has been exceeded')
    else:
        await ctx.send('Cannot vote yourself')

client.run(TOKEN)
