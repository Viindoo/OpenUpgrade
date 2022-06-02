from openupgradelib import openupgrade

_removed_model_list = [
    'procurement.order'
    ]

def delete_mail_message_with_model_removed(env):
    for model in _removed_model_list:
        if not env.__contains__(model):
            openupgrade.logged_query(
                env.cr, """
                DELETE FROM mail_message
                WHERE model = {};""".format(model))


@openupgrade.migrate()
def migrate(env, version):
    delete_mail_message_with_model_removed(env)
