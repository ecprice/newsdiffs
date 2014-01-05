for line in open('/mit/newsdiffs/.my.cnf').read().split():
    if line.startswith('password='):
        pwd = line.split('=')[1]

location = 'mysql://newsdiffs:%s@sql.mit.edu/newsdiffs+newsdiffs' % pwd
