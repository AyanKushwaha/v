#!/usr/bin/python
# -*- coding: utf-8-*-
import json
from datetime import datetime
import os
from utils.divtools import fd_parser
from carmensystems.common.ServiceConfig import ServiceConfig

json_template_taxi_bokning=u'''{
  "SUTI": {
    "orgSender": {
      "@name": "Scandinavian Airlines",
      "idOrg": {
        "@unique": "true",
        "@id": "SAS_API_0001",
        "@src": "SUTI:linkId"
      }
    },
    "orgReceiver": {
      "@name": "SAS",
      "idOrg": {
        "@unique": "true",
        "@id": "taxibokning_TaxiStockholm_0057",
        "@src": "SUTI:linkId"
      }
    },
    "msg": {
      "@msgName": "ORDER",
      "@msgType": "2000",
      "idMsg": {
        "@id": "2016110900001794",
        "@src": "SAS_API_0001:messageId"
      },
      "order": {
        "idOrder": {
          "@unique": "true",
          "@id": "UniktBokningsnummer",
          "@src": "SAS_API_0001:orderId"
        },
        "agreement": {
          "@name": "SAS",
          "idAgreement": {
            "@unique": "true",
            "@id": "SAS",
            "@src": "SVEA:agreementId"
          },
          "product": {
            "idProduct": {
              "@unique": "true",
              "@id": "FLIGHT-TRANSFER",
              "@src": "SAS:productId"
            }
          }
        },
        "process": {
          "@allowRouting": "false",
          "@preorderedVehicle": "true",
          "@report": "false",
          "@trafficControl": "false",
          "@dispatchResponsible": "provider",
          "@dispatch": "true",
          "@manualDispatch": "true"
        },
        "economyOrder": {
          "formOfPayment": {
            "payment": {
              "@paymentType": "account",
              "idPayment": {
                "@id": "22121",
                "@src": "taxibokning_api_0015:CustomerId"
              }
            }
          }
        },
        "resourceOrder": {
          "vehicle": {
            "capacity": {
              "seats": { "@noOfSeats": "1" }
            }
          }
        },
        "route": {
          "node": [
            {
              "@nodeType": "pickup",
              "@nodeSeqno": "1",
              "addressNode": {
                "@country": "Sweden",
                "@postalNo": "10327",
                "@community": "Stockholm",
                "@street": "",
                "@addressName": "Radisson Blu Hotel",
                "geographicLocation": {
                  "@precision": "1000",
                  "@long": "18.057275",
                  "@lat": "59.330147",
                  "@typeOfCoordinate": "WGS-84"
                }
              },
              "timesNode": {
                "time": {
                  "@timeType": "scheduledtime",
                  "@time": "2016-11-20T19:08:00",
                  "@timeZone": "1",
                  "@timeAccuracy": "Scheduled"
                }
              },
              "contents": {
                "content": {
                  "@name": "Filip Stjernberg",
                  "@contentType": "traveller",
                  "manualDescriptionContent": {
                    "@vehicleConfirmation": "false",
                    "@manualText": "",
                    "@sendtoOperator": "true",
                    "@sendtoVehicle": "true",
                    "@sendtoInvoice": "false"
                  },
                  "contactInfosContent": {
                    "contactInfo": {
                      "@contactInfo": "+46708408079",
                      "@contactType": "phone"
                    }
                  }
                }
              }
            },
            {
              "@nodeType": "destination",
              "@nodeSeqno": "2",
              "addressNode": {
                "@country": "Sweden",
                "@postalNo": "19060",
                "@street": "",
                "@addressName": "Arlanda Flygplats",
                "geographicLocation": {
                  "@precision": "1000",
                  "@long": "17.924194",
                  "@lat": "59.649357",
                  "@typeOfCoordinate": "WGS-84"
                }
              },
              "contents": {
                "content": {
                  "@name": "Filip Stjernberg",
                  "@contentType": "traveller",
                  "manualDescriptionContent": {
                    "@vehicleConfirmation": "false",
					"@manualText": "",
                    "@sendtoOperator": "true",
                    "@sendtoVehicle": "true",
                    "@sendtoInvoice": "false"
                  },
                  "contactInfosContent": {
                    "contactInfo": {
                      "@contactInfo": "087282630",
                      "@contactType": "phone"
                    }
                  }
                }
              }
            }
          ]
        }
      }
    }
  }
}
'''
json_template_taxi_cancelation = u'''{
  "SUTI": {
    "orgSender": {
      "@name": "Scandinavian Airlines",
      "idOrg": {
        "@unique": "true",
        "@id": "SAS_API_0001",
        "@src": "SUTI:linkId"
      }
    },
    "orgReceiver": {
      "@name": "SAS",
      "idOrg": {
        "@unique": "true",
        "@id": "taxibokning_TaxiStockholm_0057",
        "@src": "SUTI:linkId"
      }
    },
    "msg": {
      "@msgName": "CANCELLATION REQUEST",
      "@msgType": "2010",
      "idMsg": {
        "@id": "2016110900001794",
        "@src": "SAS_API_0001:messageId"
      },
      "referencesTo": {
        "idOrder": [
          {
            "@id": "UniktBokningsnummer",
            "@src": "SAS_API_0001:orderId"
          }
        ]
      }
    }
  }
}
'''


class StockholmTaxiMessageBase:
    def __init__(self):
        self.service_config = ServiceConfig()

    def getReceiver(self):
        (_, receiver_id) = self.service_config.getProperty("dig_settings/webservice/receiver_id")
        return receiver_id

    def getEconomyOrderSrc(self):
        (_, economy_order_src) = self.service_config.getProperty("dig_settings/webservice/economy_order")
        return economy_order_src

    def getEconomyOrderId(self):
        (_, economy_order_id) = self.service_config.getProperty("dig_settings/webservice/economy_order_id")
        return economy_order_id

class StockholmTaxiCancellationMessage(StockholmTaxiMessageBase):
    def __init__(self):
        StockholmTaxiMessageBase.__init__(self)
        self.msg = json.loads(json_template_taxi_cancelation)


    def createMsg(self,bookingNo):
        self.msg["SUTI"]["msg"]["idMsg"]["@id"]=unicode(makeUniqueMsgId(),"latin-1")

        self.msg["SUTI"]["orgReceiver"]["idOrg"]["@id"] = self.getReceiver()

        idOrder_list=[]
        idOrder = {
            "@id": bookingNo,
            "@src": "SAS_API_0001:orderId"
                }
        idOrder_list.append(idOrder)
        self.msg["SUTI"]["msg"]["referencesTo"]["idOrder"]=idOrder_list
        return self.msg


def makeUniqueMsgId():
    current_time = datetime.now().time()
    tmp= current_time.isoformat()
    tmp= tmp.replace(":", "")
    return  tmp.replace(".", "")

def makeUniqueOrderId(booking):
    f = fd_parser(booking.flightNr)
    flight = f.flight_descriptor
    tmp_str = flight +"-"+booking.flightDepStn+"-"+ str(booking.flightTime )+"-"+str(booking.pickUpTime)
    tmp_str =tmp_str.replace(" ","")
    return tmp_str

def ARN_time_formatted(time_str):
    dt = datetime.strptime(time_str, "%d%b%Y %H:%M")
    a = dt.strftime("%Y-%m-%dT%H:%M:00")
    return a


class StockholmTaxiBookingMessage(StockholmTaxiMessageBase):
    def __init__(self):
        StockholmTaxiMessageBase.__init__(self)
        self.msg = json.loads(json_template_taxi_bokning)


    def setMsgid(self):
        self.msg["SUTI"]["msg"]["idMsg"]["@id"]=unicode(makeUniqueMsgId(),"latin-1")

    def setorgReceiver(self):
        self.msg["SUTI"]["orgReceiver"]["idOrg"]["@id"] = self.getReceiver()

    def setBookingNumber(self,bookingNumber):
        self.msg["SUTI"]["msg"]["order"]["idOrder"]["@id"]=unicode(bookingNumber,"latin-1")

    def setNoOfPassengers(self,noOfpassengers):
        self.msg["SUTI"]["msg"]["order"]["resourceOrder"]["vehicle"]["capacity"]["seats"]["@noOfSeats"]=unicode(noOfpassengers,"latin-1")


    def setBookingType(self, noOfPassengers):
        if int(noOfPassengers) > 3:
            ro_map = self.msg["SUTI"]["msg"]["order"]["resourceOrder"]["vehicle"]
            ro_map["attributesVehicle"]=dict(attribute=dict(idAttribute={"@id" : unicode("1619", "latin-1"), "@src" : unicode("SUTI", "latin-1")}))



    def setEconomyOrder(self):
        self.msg["SUTI"]["msg"]["order"]["economyOrder"]["formOfPayment"]["payment"]["idPayment"]["@src"]=self.getEconomyOrderSrc()
        self.msg["SUTI"]["msg"]["order"]["economyOrder"]["formOfPayment"]["payment"]["idPayment"]["@id"]=self.getEconomyOrderId()

    def setPickUpaddress(self, addressName, city, postalNo, lat, long):
        self.setAddress(True,addressName,city,postalNo,lat,long)


    def setDeliveryAddress(self,addressName,city,postalNo,lat,long):
        self.setAddress(False,addressName,city,postalNo,lat,long)


    def setAddress(self,pickup,addressName,city,postalNo,lat,long):
        if pickup:
            ix=0
        else :
            ix=1
        tmp_addressName = addressName.decode("latin1")
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["addressNode"]["@addressName"]=tmp_addressName.encode("utf-8")
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["addressNode"]["@community"] = city
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["addressNode"]["@postalNo"] = postalNo
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["addressNode"]["geographicLocation"]["@lat"]= lat
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["addressNode"]["geographicLocation"]["@long"]= long



    def setPickUpTime(self,aTime):
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][0]["timesNode"]["time"]["@time"]=unicode(aTime,"latin-1")

    def setPickUpResposible(self,phoneNumber,flight,noOfPassengers):
        self.setResposible(True,phoneNumber,flight,noOfPassengers)

    def setDeliveryResponsible(self,phoneNumber,flight,noOfPassengers):
        self.setResposible(False,phoneNumber,flight,noOfPassengers)

    def setResposible(self,pickup,phoneNumber,flight,noOfPassengers):
        if pickup:
            ix=0
        else:
            ix=1

        name = "SAS Crew/"+flight+"/"+noOfPassengers+"P"
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["contents"]["content"]["@name"] = unicode(name,"latin-1")
        self.msg["SUTI"]["msg"]["order"]["route"]["node"][ix]["contents"]["content"]["contactInfosContent"]["contactInfo"][
                "@contactInfo"] = "087282630" #unicode(phoneNumber)


    def setConnection(self,from_hotel,flight):

        connection=json.loads('''{
            "@connectionType": "flight",
            "@connectionName": "SK123",
            "@connectionArrDep": "D"
            }''')
        connection["@connectionType"] =u'flight'
        connection["@connectionName"] = unicode(flight,"latin-1")
        if from_hotel:
            connection["@connectionArrDep"]=u"D" #Departure
            self.msg["SUTI"]["msg"]["order"]["route"]["node"][1]["contents"]["content"]["connection"] = connection
        else:
            connection["@connectionArrDep"]=u"A" #Arrival
            self.msg["SUTI"]["msg"]["order"]["route"]["node"][0]["contents"]["content"]["connection"] = connection


    def createMsg(self,from_hotel,bookingNumber,noOfpassengers,pickupAddressName,pickupCity,pickupPostalNo,
               pickupLat,pickupLong,pickUpTime,pickupResponsiblePhone,
               deliveryAddressName,deliveryCity,deliveryPostalNo,deliveryLat,deliveryLong,
               deliveryResponsiblePhone,flight):

        self.setMsgid()
        self.setorgReceiver()
        self.setBookingNumber(bookingNumber)
        self.setNoOfPassengers(noOfpassengers)
        self.setBookingType(noOfpassengers)
        self.setEconomyOrder()
        self.setPickUpaddress(pickupAddressName,pickupCity,pickupPostalNo,pickupLat,pickupLong)
        self.setPickUpTime(pickUpTime)
        self.setPickUpResposible(pickupResponsiblePhone,flight,noOfpassengers)
        self.setDeliveryAddress(deliveryAddressName,deliveryCity,deliveryPostalNo,deliveryLat,deliveryLong)
        self.setDeliveryResponsible("087282630",flight,noOfpassengers)
        self.setConnection(from_hotel,flight)
        return self.msg


    def createHoteltoAirportMessage(self, booking, hotel_postal_code, hotel_city, bookingManager, correctionTerm):

        orderId = makeUniqueOrderId(booking)

        pickUptime = ARN_time_formatted(str(booking.pickUpTime + correctionTerm))
        ARN_contact_info = bookingManager.getCustomerData("SKS")
        ARN_contact = ARN_contact_info.contact
        ARN_contact_phone = ARN_contact_info.phone

        if booking.flightNr.strip() == "-00001":
            booking.flightNr = "A000"
        f = fd_parser(booking.flightNr)
        flight = f.flight_id

        HotelToAirportMessage = self.createMsg(True, orderId, str(booking.crewAmount), "Scandic Grand Central", hotel_city, hotel_postal_code,
                          "59.333749", "18.055895", pickUptime, ARN_contact_phone,
                          "ARLANDA FLYGPLATS", "Sigtuna", "19060",
                          "59.649927", "17.929847",
                          ARN_contact_phone, flight)
        return HotelToAirportMessage

    def createAirporttoHotelMessage(self,booking, hotel_postal_code,hotel_city,bookingManager,correctionTerm):

        orderId = makeUniqueOrderId(booking)
        pickUptime = ARN_time_formatted(str(booking.pickUpTime)) # + correctionTerm))
        ARN_contact_info = bookingManager.getCustomerData("SKS")
        ARN_contact = ARN_contact_info.contact
        ARN_contact_phone = ARN_contact_info.phone

        if booking.flightNr.strip() == "-00001":
            booking.flightNr = "A000"
        f = fd_parser(booking.flightNr)
        flight = f.flight_id

        AirportToHotelMessage = self.createMsg(False, orderId, str(booking.crewAmount), "SAS CREWBASE", "Sigtuna", "19060",
                                  "59.649927", "17.929847", pickUptime, ARN_contact_phone,
                                  "Scandic Grand Central", hotel_city, hotel_postal_code,
                                  "59.333749", "18.055895",
                                   ARN_contact_phone, flight)
        return AirportToHotelMessage

