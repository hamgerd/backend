from django.db import models


class CommissionRulesManager(models.Manager):
    def get_commission_rule(self, amount):
        rules = self.filter(start__lte=amount, end__gt=amount)
        if rules.count() > 1:
            raise ValueError(f"Two rules matched for amount {amount}.")
        if rules.count() == 1:
            return rules[0]
        return None
