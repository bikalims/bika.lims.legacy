External methods for CRONS
==========================
<browser:page
  for="*"
  name="expire_reference_samples"
  class="bika.lims.browser.expirereferencesamples.ExpireReferenceSamplesView"
  permission="cmf.ManagePortal"
  attribute="expire_reference_samples"
  layer="bika.lims.interfaces.IBikaLIMS"
/>

CRON CALL
=========
*/5 * * * * wget --delete-after http://admin:password@127.0.0.1:8091/bika/@@expire_reference_samples
