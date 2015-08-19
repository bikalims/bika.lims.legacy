*** Settings ***

Library         BuiltIn
Library         Selenium2Library  timeout=5  implicit_wait=0.2
Library         String
Resource        keywords.txt
Resource        plone/app/robotframework/keywords.robot
Library         bika.lims.testing.Keywords
Resource        plone/app/robotframework/selenium.robot
Library         Remote  ${PLONEURL}/RobotRemote
Variables       plone/app/testing/interfaces.py
Variables       bika/lims/tests/variables.py

Suite Setup     Start browser
Suite Teardown  Close All Browsers

Library          DebugLibrary

*** Test Cases ***

Test order as LabManager
    Enable autologin as  LabManager
    Disable auto print inventory stickers
    # https://jira.bikalabs.com/browse/LIMS-1900
    Given a blank order form in supplier-3
     # Only products registered to a supplier can be ordered to him
     page should not contain  Ink cartridge black PGI-7BK
     When I enter 2 for product Nitric acid
      and I submit the new order
    subtotal is 24.22
    vat is 0.00
    total is 24.22
    Then when I trigger dispatch transition
     and I publish the order
    page should contain  Dispatched
    Then I can print the order for supplier-3
    Then when I trigger receive transition
    page should contain  Item state changed
    Then when I trigger store transition
    page should contain  Item state changed

Test product reception and storage as LabManager
    Enable autologin as  LabManager
    Disable auto print inventory stickers
    Add storage levels
    # https://jira.bikalabs.com/browse/LIMS-1936

    Given a dispatched order in supplier-3 with 5 items of Nitric acid
     When I trigger receive transition
     Then new product items appear in the list under order-1
      and quantity of the Chemical named Nitric acid supplied by supplier-3 is 5

     When I store 3 items of Nitric acid in Freezer > Drawer-1
     Then page should contain  5 (3)
      and products items are assigned to containers in Drawer-1 of Freezer
     When I store 2 items of Nitric acid in Warehouse > Row-1 > Shelf-1
     Then page should contain  5 (5)

*** Keywords ***

# --- Given ------------------------------------------------------------------

a blank order form in ${supplier_id}
    [Documentation]  Load a fresh Order form
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier_id}/portal_factory/Order/xxx/edit
    wait until page contains  xxx

a dispatched order in ${supplier_id} with ${number} items of ${product}
    Given a blank order form in ${supplier_id}
    When I enter ${number} for product ${product}
     and I submit the new order
     and I trigger dispatch transition
     and I publish the order
    Wait until page contains  Product

# --- When -------------------------------------------------------------------

I enter ${nr} for product ${product_title}
    [Documentation]  Simply input the value for this product
    input text   xpath=.//input[@data-product_title='${product_title}']   ${nr}
    press key    xpath=.//input[@data-product_title='${product_title}']   \t

I submit the new order
    [Documentation]  Save the order and wait for the submission to complete
    click button  Save
    wait until page contains  Order pending

I trigger ${transitionId} transition
    Element Should Be Visible  css=dl#plone-contentmenu-workflow span
    Element Should Not Be Visible  css=dl#plone-contentmenu-workflow dd.actionMenuContent
    Click link  css=dl#plone-contentmenu-workflow dt.actionMenuHeader a
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=dl#plone-contentmenu-workflow dd.actionMenuContent
    Click Link  workflow-transition-${transitionId}

I publish the order
    Click button  Publish

I store ${number} items of Nitric acid in ${storage}
    Go to  ${PLONEURL}/bika_setup/bika_suppliers/supplier-3/order-1
    input text  number-product-8  ${number}
    select from dropdown  storage-product-8  ${storage}
    click button  Store

# --- Then -------------------------------------------------------------------

status message should be ${message}
    wait until page contains element  css=dl.portalMessage dt  Info
    wait until page contains element  css=dl.portalMessage dd  ${message}

subtotal is ${nr}
    [Documentation]  Verify the subtotal is calculated correctly
    element text should be  css=span.subtotal  ${nr}

vat is ${nr}
    [Documentation]  Verify the vat is calculated correctly
    element text should be  css=span.vat  ${nr}

total is ${nr}
    [Documentation]  Verify the total is calculated correctly
    element text should be  css=span.total  ${nr}

I can print the order for ${supplier_id}
    Page Should contain Link  ${PLONEURL}/bika_setup/bika_suppliers/${supplier_id}/order-1/print
    # Can't display print here, as Robot framework can't close the print dialog box once it opens!

new product items appear in the list under ${order_id}
    go to  ${PLONEURL}/bika_setup/bika_productitems
    page should contain  ${order_id}

quantity of the ${category} named ${product} supplied by ${supplier} is ${quantity}
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/products
    click element  xpath=//th[contains(@cat, '${category}')]
    click link  ${product}

I can print stickers by clicking an icon in ${order} of ${supplier}
    go to  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/${order}
    click element  //img[@title='Small Sticker']
    location should be  ${PLONEURL}/bika_setup/bika_suppliers/${supplier}/${order}/stickers

products items are assigned to containers in Drawer-1 of Freezer
    go to  ${PLONEURL}/bika_setup/bika_storageunits
    click link  Freezer
    click link  Drawer-1
    page should contain  P-0001
    page should contain  P-0003

# --- Other -------------------------------------------------------------------

Add storage levels
    Add Freezer as storage unit
    Add 3 storage levels with title Drawer
    click link  Drawer-1
    Add 10 storage levels with title Container

    Add Warehouse as storage unit
    Add 2 storage levels with title Row
    click link  Row-1
    Add 2 storage levels with title Shelf
    click link  Shelf-1
    Add 10 storage levels with title Container
    Go to Shelf-2 in Row-1 of Warehouse
    Add 10 storage levels with title Container

Disable auto print inventory stickers
    go to  ${PLONEURL}/bika_setup/
    click link  Inventory
    unselect checkbox  css=#AutoPrintInventoryStickers
    click button  Save
    wait until page contains  saved


Add ${title} as storage unit
    go to  ${PLONEURL}/bika_setup/bika_storageunits/portal_factory/StorageUnit/xxx/edit
    wait until page contains  xxx
    input text  css=#title  ${title}
    click button  Save
    wait until page contains  saved

Add ${number} storage levels with title ${title}
    input text  css=.storagelevel-title  ${title}
    input text  css=.storagelevel-number  ${number}
    click button  Add storage levels
    wait until page contains  saved

Go to ${level2} in ${level1} of ${storageunit}
    Go to  ${PLONEURL}/bika_setup/bika_storageunits
    click link  ${storageunit}
    click link  ${level1}
    click link  ${level2}
