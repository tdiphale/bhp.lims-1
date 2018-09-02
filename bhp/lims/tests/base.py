# -*- coding: utf-8 -*-

import unittest2 as unittest
from bika.lims.testing import BASE_LAYER_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.testing import z2


class SimpleTestLayer(PloneSandboxLayer):
    """Setup Plone with installed AddOn only
    """
    defaultBases = (BASE_LAYER_FIXTURE, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(SimpleTestLayer, self).setUpZope(app, configurationContext)

        # Load ZCML
        import archetypes.schemaextender
        import bika.lims
        import senaite.lims
        import bhp.lims

        self.loadZCML(package=archetypes.schemaextender)
        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.lims)
        self.loadZCML(package=bhp.lims)

        # Install product and call its initialize() function
        z2.installProduct(app, "bhp.lims")

    def setUpPloneSite(self, portal):
        super(SimpleTestLayer, self).setUpPloneSite(portal)

        # Apply Setup Profile (portal_quickinstaller)
        applyProfile(portal, "bika.lims:default")
        applyProfile(portal, "senaite.lims:default")
        applyProfile(portal, "bhp.lims:default")

        login(portal.aq_parent, SITE_OWNER_NAME)

        # Add some test users
        for role in (
                "LabManager",
                "LabClerk",
                "Analyst",
                "Verifier",
                "Sampler",
                "Preserver",
                "Publisher",
                "Member",
                "Reviewer",
                "RegulatoryInspector"):
            for user_nr in range(2):
                if user_nr == 0:
                    username = "test_%s" % (role.lower())
                else:
                    username = "test_%s%s" % (role.lower(), user_nr)
                try:
                    member = portal.portal_registration.addMember(
                        username,
                        username,
                        properties={
                            "username": username,
                            "email": username + "@example.com",
                            "fullname": username}
                    )
                    # Add user to all specified groups
                    group_id = role + "s"
                    group = portal.portal_groups.getGroupById(group_id)
                    if group:
                        group.addMember(username)
                    # Add user to all specified roles
                    member._addRole(role)
                    # If user is in LabManagers, add Owner local role on
                    # clients folder
                    if role == "LabManager":
                        portal.clients.manage_setLocalRoles(username,
                                                            ["Owner", ])
                except ValueError:
                    pass  # user exists

        # Force the test browser to show the site always in 'en'
        ltool = portal.portal_languages
        ltool.manage_setLanguageSettings(
            "en", ["en"], setUseCombinedLanguageCodes=False, startNeutral=True)

    logout()


###
# Use for simple tests (w/o contents)
###
SIMPLE_FIXTURE = SimpleTestLayer()
SIMPLE_TESTING = FunctionalTesting(
    bases=(SIMPLE_FIXTURE, ),
    name="bhp.lims:SimpleTesting"
)


class SimpleTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])
