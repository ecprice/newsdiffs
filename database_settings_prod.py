for line in open('/mit/ecprice/.my.cnf').read().split():
    if line.startswith('password='):
        pwd = line.split('=')[1]

location = 'mysql://ecprice:%s@sql.mit.edu/ecprice+newsdiffs' % pwd
