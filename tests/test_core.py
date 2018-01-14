# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
import redis
import consul
import threading, queue
import time
import hashlib
import os
import sys
sys.path.insert(0, "../")
sys.path.insert(0, ".")
import local_tools
from lings import routeling
from lings import routeling_basic_operations

@pytest.fixture(scope='session')
def redis_connection():
    redis_ip,redis_port = local_tools.lookup('redis')
    r = redis.StrictRedis(host=redis_ip, port=str(redis_port),decode_responses=True)
    yield r

def listen(listen_on,listen_for,q,redis_connection):
    print("listening for {}".format(repr(listen_for)))
    pubsub = redis_connection.pubsub()
    pubsub.subscribe(listen_on)
    for item in pubsub.listen():
        if item['data'] != 1:
            print("received {} on {}".format(item['data'],item['channel']))
            assert item['data'] == listen_for
            #return with queue to assert in test_ function
            q.put(item['data'])
            break

def test_routing(redis_connection):
    # send a message through a set of routes
    # listen on endpoint for message
    #
    # core machine must be running
    # 
    # Troubleshooting:
    # redis:
    #     config set protected-mode off 
    # nomad/python:
    #     packages must be installed using 
    #     'sudo pip3 install' since those 
    #     installed with --user are not accessible
    #     ^ TODO figure out a more elegant solution
    #     ^ for this...

    message = "hello world"
    endpoint = "/baz"
    startpoint = "/foo"
    q = queue.Queue()
    t = threading.Thread(name='listener', target=listen,args=(endpoint,message,q,redis_connection,))
    print("starting listener thread")
    t.start()

    # add two routes that chain together
    route_1 = "if '/foo' do mapii '/bar'"
    route_2 = "if '/bar' do mapii '/baz'"
    routeling.add_route(route_1)
    routeling.add_route(route_2)
    # send the message internal_to_internal
    # currently this means redis publish to redis channel
    routeling_basic_operations.sendi(startpoint,message)

    # there is a slight latency for routing
    # so do not remove routes immediately
    time.sleep(1)
    endpoint_result = q.get()
    assert message == endpoint_result

    route1_hash = hashlib.sha224((route_1+"\n").encode()).hexdigest()

    assert routeling.get_routes()

    hash_substr_found = False
    for route in routeling.get_routes():
        if route1_hash in route:
            hash_substr_found = True

    assert hash_substr_found
    assert routeling.get_route(route_1+"\n") 

    # remove routes
    routeling.remove_route(route_1)
    routeling.remove_route(route_2)
    # join thread
    # TODO fail on timeout
    t.join(4)
    assert not t.is_alive()

def test_machine_scheduled_running(machine_yaml):

    # pytest may be run insides tests directory
    # or main directory of project
    if not os.path.isfile(machine_yaml):
        if os.path.isfile("../"+machine_yaml):
            machine_yaml = "../"+machine_yaml
    
    assert os.path.isfile(machine_yaml)

    machine_scheduled_components = local_tools.lookup_machine(machine_yaml,ignored_services=[])
    
    for k,v in machine_scheduled_components.items():
        assert (k != "") and (v == "running")
    
    assert(set(list(machine_scheduled_components.values()))) == set(list(["running"]))
