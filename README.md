
## Installation

Setup:

  ```
  python setup.py develop
  ```

## Usage

First set environment variable for commerce

```
os.environ['TBK_COMMERCE_KEY'] = "KEY"
os.environ['TBK_COMMERCE_CRT'] = "CERTIFICATE"
```
Init Inscription

```
#  request
oneclick = OneClick()
resp = oneclick.init_inscription(email='your@email.com', 
                                 redirect_url='http://your_domain.com',
                                 username='your_username')
#  response example
resp.is_valid()  # True
resp.token  # e7665f871fa39e6c05549eeddd1ff07a520a769fa84cc6994465cdb06cbb4b
resp.urlWebpay  # https://webpay3g.orangepeople.cl/webpayserver/bp_inscription.cgi
```
Finish Inscription

```
oneclick = OneClick()
#  Transbank send the TBK_TOKEN to the redirect_url given on init_inscription
resp = oneclick.finish_inscription(token=params['TBK_TOKEN'])
#  response example
resp.is_valid()  # True
resp.authCode  # 1234
resp.creditCardType  # Visa
resp.last4CardDigits  # 6623
resp.tbkUser  # d2f27f36-b038-4937-8aa6-182b3de38cfd
```
Authorize

```
oneclick = OneClick()
#  request
resp = oneclick.authorize(amount_to_charge=10000, 
                          tbk_user='d2f27f36-b038-4937-8aa6-182b3de38cfd',
                          username='your_username', 
                          buy_order='20150820155538859')
#  response example
resp.is_valid()  # True
resp.authorizationCode  # 1213
resp.transactionId  #  71498
resp.creditCardType  #  Visa
resp.last4CardDigits  #  6623
```
Reverse

```
oneclick = OneClick()
#  request
resp = oneclick.reverse(buy_order='20150820155538859')
#  response example
resp.is_valid()  # True
resp.reverseCode  # 3619160862457231902
resp.reversed  # True
```
remove user

```
oneclick = OneClick()
#  request
resp = oneclick.remove_user(tbk_user='d2f27f36-b038-4937-8aa6-182b3de38cfd', 
                            username='your_username')
#  response example
resp.is_valid()  # True
resp.removed  # True
```


## Tests

  ```
  python setup.py test
  ```

  ```
  nosy
  ```  

## Contributors

You can contribute by forking the project, adding the contributions and creating the PRs, or just file an issue and we will try to solve it ASAP.


## License

The MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.