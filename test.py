
def find_group(start,end):
  first_page = ((start-1)//175)+1
  last_page = ((end-1)//175)+1
  return range(first_page,last_page+1)


print(find_group(1,50))