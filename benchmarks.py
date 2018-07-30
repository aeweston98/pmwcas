import subprocess
import os
import signal
import time

def run(threads, size, output):
	server = subprocess.Popen(['./mwcas_shm_server','-shm_segment','\"mwcas\"','-array_size', str(size)],shell=False, preexec_fn=os.setsid)
	benchmark = subprocess.Popen(['./mwcas_benchmark','-shm_segment', '\"mwcas\"','-threads',str(threads),'-seconds','5','-array_size',str(size),'-word_count','4'], shell=False, stdout=subprocess.PIPE, preexec_fn=os.setsid)
	
	count = 0
	while True:
		if(count > 2):
			os.killpg(os.getpgid(benchmark.pid),signal.SIGTERM)
			break
		elif(benchmark.poll() == None):
			count += 1
			time.sleep(5)
		else:
			output.append((size,threads,benchmark.stdout.read()))
			break
		
	os.killpg(os.getpgid(server.pid), signal.SIGTERM)

def parse(output):
	
	dump = open('raw_data.txt', 'w')
	f = open('parsed_data.txt', 'w')
	for (threads,size,text) in output:
		dump.write(text + '\n')
		attempted = [x for x in text.split('\n') if 'ops/sec' in x]
		successful = [x for x in text.split('\n') if 'updates/sec' in x]
		if(len(attempted) > 0):
			val_att = attempted[0].split(' ')[1]
			val_suc = successful[0].split(' ')[1]
			f.write(str(threads)+','+str(size)+','+str(val_suc)+','+str(val_att)+'\n')

	dump.close()
	f.close()


if __name__ == "__main__":
	threads = [2,4,6,8]
	sizes = [10,25,100]
	output = []
	
	#run(4,100,output)
	#run(8,1000000,output)
	#parse(output)
	for i in range(len(threads)):
		for j in range(len(sizes)):
			for k in range(1):
				run(threads[i], sizes[j], output)

	parse(output)
