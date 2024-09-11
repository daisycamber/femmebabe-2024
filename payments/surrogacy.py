def save_and_send_agreement(mother, parent):
    from payments.agreements import generate_surrogacy_agreement
    text = render_agreement(mother.verifications.last().full_name, parent, mother)
    path = generate_surrogacy_agreement(parent.verifications.last().full_name.replace(' ', '_') + '-x-' + mother.verifications.last().full_name.replace(' ', '_'), text, [parent, None, mother, None])
    from .models import SurrogacyAgreement
    a = SurrogacyAgreement.objects.create(intended_parent=parent, mother=mother, agreement=path, signed=True)
    from users.email import send_html_email_template
    send_html_email_template(parent, 'Expected Parent, Here is Your Surrogacy Agreement from {}'.format(settings.SITE_NAME), 'Dear {}\n'.format(parent.verifications.last().full_name) + 'Attached is your copy of the surrogacy agreement you signed with {}. This agreement will be carried out within one year.\n'.format(mother.verifications.last().full_name) + 'Thank you for your loyalty and we look forward to working with you. We will be in touch soon to organize details for medical procedures.\nSincerely, {}'.format(settings.SITE_NAME), attachments=[path])
    send_html_email_template(mother, 'Expected Mother, Here is Your Surrogacy Agreement from {}'.format(settings.SITE_NAME), 'Dear {}\n'.format(mother.verifications.last().full_name) + 'Attached is your copy of the surrogacy agreement you signed with {}. This agreement will be carried out within one year.\n'.format(parent.verifications.last().full_name) + 'Thank you for your loyalty and we look forward to working with you. We will be in touch soon to organize details for medical procedures.\nSincerely, {}'.format(settings.SITE_NAME), attachments=[path])
    a.sent = True
    a.save()
