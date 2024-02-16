# Expresslink

## quick info

charset = ISO 8859-1

- The character set supported by expressLink is ISO 8859-1.
- Disallowed characters with diacritic marks should be replaced with standard Latin equivalent.     
  For example, Å becomes A, ñ becomes n.

## Available Services

### `Create shipment`

- Use to ship domestic items and request a shipment number
- Use to ship international export items and request a shipment number
- Request an ad-hoc domestic or international collection

### `(Re)print label`

- Use to print labels for domestic and international shipments, including routing labels
  for third parties e.g. GLS and FedEx, and to print undated returns labels.

### `Print document`

- Use to print customs documentation for international non-document shipments

### `Create manifest`

- Allocate shipment to either an international or domestic manifest
- Print manifest
- Print manifest once it has been created

### `Return Shipment`

- Activates a previously created undated domestic collection request by shipment
  number.

### `Find`

- Use to search for and retrieve information to be included in Delivery Options requests

### `Cancellation`

- Use to cancel a Domestic or International delivery prior to the Create Manifest request

### `CreatePrint`

- Use for delivery only to ship domestic items to request a shipment number and

### `generate XML data stream label response`

- Use for delivery only to ship international items to request a shipment number and
  generate XML data stream label response

### `CCReserve`

- Used to create Convenient Collect PostOfficeID - NOTE : This is not currently required
  when creating a Convenient Collect shipment

------------------------------------


## XML Request Field Descriptions

The following descriptions may be used in describing the contents of a field:

### `Max Length`

Maximum number of characters, including spaces. Minimum length
is assumed to be 1 for mandatory fields and 0 for optional fields

### `Mandatory`

Field always required

### `Mandatory*`

Field required dependent on another field being populated with a
specific value

### `Optional`

A non-mandatory field

### `Numeric`

Numbers only

### `Alphanumeric`

Numbers and letters

### `Date`

Date format required

------------------------------------

## Escaping

Unless specifically advised otherwise, the field contents are case sensitive.
In XML requests, there are 5 characters which much be escaped before the request is sent.
These are listed below with their escaped notation for reference:

| Character | Escaped Notation |
|-----------|------------------|
| &         | `&amp;`          |
| "         | `&quot;`         |
| '         | `&apos;`         |
| <         | `&lt;`           |
| >         | `&gt;`           |

<CR/LF> should not be included in any field as this can cause files to be rejected in the
Parcelforce down stream systems

## Connecting to expressLink

### Dev Environment

#### Endpoint

https://expresslink-test.parcelforce.net/ws/

#### WSDL namespace

http://www.parcelforce.net/ws/ship/V14
A local copy of the latest WSDL will be provided by the Parcelforce Customer
Solutions team at the start of an integration project.

#### View Test Shipments

https://wdmo-test.parcelforce.net

### Production Environment

#### Endpoint

https://expresslink.parcelforce.net/ws
(this is the endpoint for web service requests only)

#### WSDL namespace

http://www.parcelforce.net/ws/ship/V14 PRODUCTION
See expresslink WSDL schema procided by Parcelforce

#### View Live Shipments

https://www.parcelforce.net/
NOTE: The WDMO expressLink GUI is not available for the CreatePrint Request

## Addressing

### `6.20.2 Specified Neighbour Request Detail`

The lookup function is called PAF. By submitting a single valid UK postcode valid PAF
addresses close to the postcode will be returned.

| Field Name | Max Length | Format               | Mandatory / optional | Details                                                              |
|------------|------------|----------------------|----------------------|----------------------------------------------------------------------|
|            |            | **Authentication**   |                      |                                                                      |
| User Name  | 80         | Alphanumeric         | Mandatory            | As provided by Parcelforce Worldwide; case sensitive                 |
| Password   | 80         | Alphanumeric         | Mandatory            | As provided by Parcelforce Worldwide; case sensitive                 |
|            |            | **Find PAF Request** |                      |                                                                      |
| Postcode   | 16         | Alphanumeric         | Mandatory            | Acceptable postcode format as per Supporting Information, must exist |
| Count      | 2          | Numeric              |                      | Returns the number of addresses specified in the <Count> field       |

### `6.20.3 Specified Neighbour Response Detail`

The following fields will be included in the response:

| Field Name          | Max Length | Format       | Details                                                                                                                 |
|---------------------|------------|--------------|-------------------------------------------------------------------------------------------------------------------------|
|                     | **PAF**    |              |                                                                                                                         |
| Postcode            | 8          | Alphanumeric | The Postcode from the request                                                                                           |
| Count               | 2          | Numeric      | Returns the number of addresses specified in the <Count> field                                                          |
| Specified Neighbour |            |              |                                                                                                                         |
| AddressLine1        | 40         | Alphanumeric | The first address line from the PAF data returned This information used in Create Shipment Specified Neighbour Request  |
| AddressLine2        | 40         | Alphanumeric | The second address line from the PAF data returned This information used in Create Shipment Specified Neighbour Request |
| AddressLine3        | 40         | Alphanumeric | The third address line from the PAF data returned This information used in Create Shipment Specified Neighbour Request  |
| Town                | 30         | Alphanumeric | The town name from the PAF data returned This information used in Create Shipment Specified Neighbour Request           |
| Postcode            | 8          | Alphanumeric | The post code from the PAF data returned This information used in Create Shipment Specified Neighbour Request           |
| Country             | 2          | Alphanumeric | The country code from the PAF data returned This information used in Create Shipment Specified Neighbour Request        |

### `Specified Post Office Request Detail`

The lookup function will return a list of Post Offices options.

| Field Name                     | Max Length | Format         | Mandatory / optional | Details                                              |
|--------------------------------|------------|----------------|----------------------|------------------------------------------------------|
|                                |            | Authentication |                      |                                                      |                                                      
| User Name                      | 80         | Alphanumeric   | Mandatory            | As provided by Parcelforce Worldwide; case sensitive |                 |            |              |                      |                                                      |
| Password                       | 80         | Alphanumeric   | Mandatory            | As provided by Parcelforce Worldwide; case sensitive |
| Specified Post Office Postcode | -          | -              | Mandatory            | -                                                    |
| Count                          | -          | -              | Optional             | -                                                    |

### `Specified Post Office Response Detail`

The following fields will be included in the response:

| Field Name                     | Max Length | Format       | Details                                                      |
|--------------------------------|------------|--------------|--------------------------------------------------------------|
| Specified Post Office Postcode | 8          | Alphanumeric | The Postcode from the request                                |
| Count                          | -          | -            | Count of Post Offices in the response                        |
| Business                       | 40         | Alphanumeric | The business name of the Post Office                         |
| AddressLine1                   | 40         | Alphanumeric | The first address line of Post Office                        |
| AddressLine2                   | 40         | Alphanumeric | The second address line of the Post Office                   |
| AddressLine3                   | 40         | Alphanumeric | The third address line of the Post Office                    |
| Town                           | 30         | Alphanumeric | The town name of the Post Office                             |
| Postcode                       | 8          | Alphanumeric | The post code of the Post Office                             |
| Country                        | 2          | Alphanumeric | The country code of Post Office                              |
| Day of the Week                | 3          | Date         | DDD - The day of the week to which the opening hours relate. |
| Open                           | 5          | Time         | Opening time                                                 |
| Close                          | 5          | Time         | Closing time                                                 |
| CloseLunch                     | 5          | Time         | Closing time for lunch                                       |
| AfterLunchOpening              | 5          | Time         | Reopening time after lunch                                   |
| Count                          | 2          | Numeric      | Count of Post Offices in the response                        |

### `Postcode Exclusion Request Detail`

The lookup function will return a list of available services per department for the Postcode
entered for the delivery and/or the collection of a parcel.

| Field Name         | Max Length | Format         | Mandatory / optional | Details                                              |
|--------------------|------------|----------------|----------------------|------------------------------------------------------|
|                    |            | Authentication |                      |                                                      |
| User Name          | 80         | Alphanumeric   | Mandatory            | As provided by Parcelforce Worldwide; case sensitive |
| Password           | 80         | Alphanumeric   | Mandatory            | As provided by Parcelforce Worldwide; case sensitive |
| Postcode           | 8          | Alphanumeric   | Optional             | The Postcode from the request                        |
| CollectionPostcode | 8          | Alphanumeric   | Optional             | The Postcode from the request                        |

### `Postcode Exclusion Response Detail`

The following fields will be included in the response:

| Field Name          | Max Length | Format       | Details                       |
|---------------------|------------|--------------|-------------------------------|
| Postcode Exclusions |            |              |                               |
| DeliveryPostcode    | 8          | Alphanumeric | The Postcode from the request |
| DepartmentID        | 25         | Alphanumeric | The Department ID             |
| ServiceCodes        | 25         | Alphanumeric | The Service Codes             |


