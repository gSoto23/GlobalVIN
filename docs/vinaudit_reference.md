# Referencia de API: VinAudit JSON payload

Este archivo contiene el equivalente exacto a la respuesta JSON generada por la API de producción de VinAudit para el VIN **JTHBK1GG3E2131249** (Lexus ES 350, 2014) con alertas de chatarra (Salvage).

Esta referencia se usa para documentar los campos y listas que `GlobalVIN` procesa durante su normalización de datos.

```json
{
  "status": "success",
  "data": {
    "id": "gerardo@gs.858703194454",
    "vin": "JTHBK1GG3E2131249",
    "date": "2026-03-02 15:03:27 PST",
    "attributes": {
      "vin": "JTHBK1GG3E2131249",
      "trim_id": "2014_lexus_es_350",
      "year": "2014",
      "make": "Lexus",
      "model": "ES",
      "trim": "350",
      "engine": "3.5L V6",
      "made_in": "Japan",
      "style": "No data",
      "steering_type": "Rack & Pinion",
      "anti-brake_system": "4-Wheel ABS",
      "fuel_type": "Gasoline",
      "fuel_capacity": "17.20 gallons",
      "gross_vehicle_weight_rating": "4696 pounds",
      "overall_height": "57.10 inches",
      "overall_length": "192.70 inches",
      "overall_width": "71.70 inches",
      "standard_seating": "5",
      "optional_seating": "No data",
      "highway_mileage": "31 miles/gallon",
      "city_mileage": "21 miles/gallon",
      "invoice_price": "$34,162",
      "manufacturer_suggested_retail_price": "$36,470"
    },
    "titles": [
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2024-11-08",
        "meter": "102984",
        "meter_unit": "M",
        "current": true
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2023-01-12",
        "meter": "77022",
        "meter_unit": "M",
        "current": false
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2022-12-14",
        "meter": "76773",
        "meter_unit": "M",
        "current": false
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2017-01-17",
        "meter": "14466",
        "meter_unit": "M",
        "current": false
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2014-09-11",
        "meter": "8",
        "meter_unit": "M",
        "current": false
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "state": "CA",
        "date": "2014-09-09",
        "meter": "8",
        "meter_unit": "M",
        "current": false
      }
    ],
    "checks": [
      {
        "brander_code": "CA",
        "brander_name": "CALIFORNIA",
        "brand_code": "09",
        "brand_title": "Rebuilt",
        "date": "2023-01-12",
        "brander_type": "State"
      },
      {
        "brander_code": "CA",
        "brander_name": "CALIFORNIA",
        "brand_code": "11",
        "brand_title": "Salvage: Damage or Not Specified",
        "date": "2022-12-14",
        "brander_type": "State"
      }
    ],
    "jsi": [
      {
        "brander_code": "P000032",
        "brander_name": "I.E.A.C.",
        "brander_city": "COSTA MESA",
        "brander_state": "CA",
        "brander_phone": "3102175200",
        "date": "2022-11-22",
        "record_type": "Junk And Salvage",
        "vehicle_disposition": "SOLD",
        "intended_for_export": "N"
      },
      {
        "brander_code": "P000032",
        "brander_name": "I.E.A.C.",
        "brander_city": "COSTA MESA",
        "brander_state": "CA",
        "brander_phone": "3102175200",
        "date": "2022-11-22",
        "record_type": "Junk And Salvage",
        "vehicle_disposition": "TO BE DETERMINED",
        "intended_for_export": "N"
      }
    ],
    "accidents": [],
    "sales": [
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2016-12-17",
        "type": "sale",
        "listing_price": "$30,652",
        "vehicle_mileage": "14,429 miles",
        "vehicle_year": "2014",
        "vehicle_make": "lexus",
        "vehicle_model": "ES 350",
        "vehicle_color": "Gray",
        "vehicle_style": "Sedan",
        "drivetrain": "FWD",
        "vehicle_doors": "4",
        "fuel_type": "Gasoline",
        "seller_type": "Dealer",
        "seller_name": "Newport Lexus",
        "seller_city": "Newport Beach",
        "seller_address": "3901 Macarthur Blvd",
        "seller_country": "USA",
        "seller_state": "CA",
        "seller_websites": "http://www.newportlexus.com"
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2016-12-31",
        "type": "sale",
        "listing_price": "$30,652",
        "vehicle_mileage": "14,429 miles",
        "vehicle_year": "2014",
        "vehicle_make": "lexus",
        "vehicle_model": "ES 350",
        "vehicle_color": "Gray",
        "vehicle_style": "Sedan",
        "drivetrain": "FWD",
        "vehicle_doors": "4",
        "fuel_type": "Gasoline",
        "seller_type": "Dealer",
        "seller_name": "Newport Lexus",
        "seller_city": "Newport Beach",
        "seller_address": "3901 Macarthur Blvd",
        "seller_country": "USA",
        "seller_state": "CA",
        "seller_websites": "http://www.newportlexus.com"
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2024-08-11",
        "type": "sale",
        "listing_price": "$11,995",
        "vehicle_mileage": "100,000 miles",
        "vehicle_year": "2014",
        "vehicle_make": "Lexus",
        "vehicle_model": "ES",
        "vehicle_trim": "ES 350 Sedan 4D",
        "vehicle_color": "grey",
        "vehicle_title": "2014 Lexus ES \u00c2\u00b7 ES 350 Sedan 4D",
        "seller_type": "Private",
        "seller_name": "Arra Oskanian",
        "seller_city": "San Diego",
        "seller_country": "USA",
        "seller_state": "CA"
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2024-09-09",
        "type": "sale",
        "listing_price": "$11,995",
        "vehicle_mileage": "100,000 miles",
        "vehicle_year": "2014",
        "vehicle_make": "Lexus",
        "vehicle_model": "ES",
        "vehicle_trim": "ES 350 Sedan 4D",
        "vehicle_color": "grey",
        "vehicle_title": "2014 Lexus ES \u00c2\u00b7 ES 350 Sedan 4D",
        "seller_type": "Private",
        "seller_name": "Arra Oskanian",
        "seller_city": "San Diego",
        "seller_country": "USA",
        "seller_state": "CA"
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2024-09-18",
        "type": "sale",
        "listing_price": "$11,995",
        "vehicle_mileage": "100,000 miles",
        "vehicle_year": "2014",
        "vehicle_make": "Lexus",
        "vehicle_model": "ES",
        "vehicle_trim": "ES 350 Sedan 4D",
        "vehicle_color": "grey",
        "vehicle_title": "2014 Lexus ES \u00c2\u00b7 ES 350 Sedan 4D",
        "seller_type": "Private",
        "seller_name": "Arra Oskanian",
        "seller_city": "San Diego",
        "seller_country": "USA",
        "seller_state": "CA"
      },
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2024-09-27",
        "type": "sale",
        "listing_price": "$11,995",
        "vehicle_mileage": "100,000 miles",
        "vehicle_year": "2014",
        "vehicle_make": "Lexus",
        "vehicle_model": "ES",
        "vehicle_trim": "ES 350 Sedan 4D",
        "vehicle_color": "grey",
        "vehicle_title": "2014 Lexus ES \u00c2\u00b7 ES 350 Sedan 4D",
        "seller_type": "Private",
        "seller_name": "Arra Oskanian",
        "seller_city": "San Diego",
        "seller_country": "USA",
        "seller_state": "CA"
      }
    ],
    "salvage": [
      {
        "vin": "JTHBK1GG3E2131249",
        "date": "2022-12-21",
        "type": "salvageAuction",
        "location": "ACE - Carson CA",
        "primary_damage": "Rear",
        "secondary_damage": "Right rear",
        "milage": "76773 mi",
        "title_type": "Salvage certificate California",
        "color": "Gray",
        "estimated_damage": "$0",
        "loss_type": "Collision",
        "keys_present": "Present"
      }
    ],
    "thefts": [],
    "lie": [],
    "mode": "prod",
    "clean": false,
    "error": "",
    "success": true
  }
}
```
