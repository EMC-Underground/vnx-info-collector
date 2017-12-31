#!/usr/bin/env python2

import os
import json
import logging
import coloredlogs
import requests
import sys
import time
from storops import VNXSystem


start_time = time.time()

# First we read in the environement variables telling us a VNX IP address,
# username, password and where we want to send the information to (API endpoint)

array_ip        = os.environ['ARRAY_IP']
username        = os.environ['USERNAME']
password        = os.environ['PASSWORD']
target_api_url  = os.environ['TARGET_API_URL']

# Setup the logger as alfred
alfred = logging.getLogger("VNX_Collector")
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=alfred)
alfred.info("Begining VNX_Collector script")


def send_to_target_api(payload):
    """Method to send full payload to API endpoint

    Sends the payoad to the api endpoint specificied in our
    environement variable captured in the begining of the script.
    This should be the last method called in the logic.

    Args:
        payload: json object containing the fields required by our storage API

    Returns:
        None
    """
    alfred.info("Making post request to: {0}".format(target_api_url))
    try:
        r = requests.post(target_api_url, data=payload)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        alfred.critical("Critical error trying to post to api: {0}".format(e))
    except requests.exceptions.HTTPError as err:
        alfred.error("HTTP error trying to post to api: {0}".format(err))

def stringify_storops(property):
    """Method to transform the properties of storops into simple strings

    Take a storops property and transform the JSON value to a string.
    Then take the string and remove the extra set of quotes to create a simple
    string.

    Args:
        propery: This should be a single property from storops

    Returns:
        A stringified version of the storops property
    """
    transformed_property = json.dumps(property)

    output = transformed_property.replace('"', '')

    alfred.debug("Stringifying: {0} to {1}".format(property, output))

    return(output)

def calculate_capacities(pools):
    """This method taks the outout of the get_pools() call and returns a dict
    of all the desired capacity values in TB form. This allows us to populate
    several values with only one call to the array.

    Args:
        pools: The output of the storops get_pool() method

    Returns:
        A dict with usable_tb, available_tb, and consumed_tb key/value pairs
    """

    alfred.debug("Here is the list of VNX Pools {0}".format(json.dumps(pools)))
    # create empty dict
    output = {}
    properties = {}

    # Create a properties map of our values as the key and storops value as the
    # value
    properties["available_tb"]  = "available_capacity_gbs"
    properties["consumed_tb"]   = "consumed_capacity_gbs"
    properties["usable_tb"]     = "user_capacity_gbs"

    for pool in pools["VNXPoolList"]:
        for key, value in properties.iteritems():
            if key in output:
                output[key] += pool["VNXPool"][value]/1024
            else:
                output[key] = pool["VNXPool"][value]/1024
    return(output)

# Create VNX object
vnx = VNXSystem(array_ip,username,password)
alfred.info("Collecting information of Array: {0}"
            .format(stringify_storops(vnx.name)))

# Create empty dictionary of the eventual payload
array_details = {}

# Collect necessary properties with as few calls to the array as required
# The vnx object has a base set of cached properties and only makes the call
# once. get_pool() makes a call each time so we call it once and parse out all
# of the data in a method call

array_details["array_name"]                 = stringify_storops(vnx.name)
array_details["serial_number"]              = stringify_storops(vnx.serial)
array_details["vendor"]                     = "DellEMC"
array_details["model"]                      = stringify_storops(vnx.model)
array_details["tier"]                       = "Standard"

alfred.debug("Midpoint: Current payload {0}".format(array_details))
# Calculate capacities
capacities = calculate_capacities(json.loads(vnx.get_pool().json()))

array_details["capacity"]                   = {}
array_details["capacity"]["usable_tb"]      = capacities["usable_tb"]
array_details["capacity"]["available_tb"]   = capacities["available_tb"]
array_details["capacity"]["consumed_tb"]    = capacities["consumed_tb"]

alfred.debug("Getting read to send payload to API endpoint. "+
            "Here is the payload: {0}".format(array_details))

# Post the array_details to the API Endpoint
send_to_target_api(array_details)

alfred.info("Finished VNX_Collector script in {0} seconds".format("%.3f" % (time.time() - start_time)))
