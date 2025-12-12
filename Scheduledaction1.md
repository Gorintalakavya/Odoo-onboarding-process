Step 1 : Login to odoo
Step 2 : Click on Settings module
Step 3 : Click on Technical
Step 4 : In Technical click on Automation
Step 5 : Click on Scheduled Actions
Step 6 : In that Select Employee created email
Code :
# Find applicants in "Onboarding Completed" stage
domain = [('stage_id.name', 'ilike', 'Onboarding Completed')]
applicants = env['hr.applicant'].search(domain)

for applicant in applicants:

    if not applicant.email_from:
        continue

    # Generate unique token or use applicant ID for secure links
    applicant_token = str(applicant.id)  # In production, use a proper token system
    
    # Email content with interactive Onboarding Plan
    subject = "Onboarding Process Initiation for %s" % (applicant.job_id.name or 'your position')
    body = (
        "<p>Dear %s,</p>"
        "<p>We are pleased to inform you that your onboarding process for "
        "<b>%s</b> is now completed.</p>"
        
        "<h3>Your Onboarding Plan Overview</h3>"
        "<p><strong>Activities To Complete:</strong></p>"
        "<ul>"
        "<li>Setup IT Materials</li>"
        "<li>Provide Bank Account Details</li>"
        "<li>Plan Training</li>"
        "<li>Complete Training</li>"
        "</ul>"
        
        "<p><strong>Documents Required - Click to Action:</strong></p>"
        "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef;'>"
        
        "<div style='margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #007bff;'>"
        "<strong>📷 Upload Address Proof</strong><br/>"
        "<div style='margin-top: 8px;'>"
        "<a href='%s/upload/address-proof/%s' style='background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📁 Upload File</a>"
        "<a href='%s/add-note/address-proof/%s' style='background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📝 Add Note</a>"
        "<a href='%s/track-task/address-proof/%s' style='background: #ffc107; color: black; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>✅ Track Task</a>"
        "</div>"
        "</div>"
        
        "<div style='margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #28a745;'>"
        "<strong>🖼️ Upload Photo</strong><br/>"
        "<div style='margin-top: 8px;'>"
        "<a href='%s/upload/photo/%s' style='background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>🖼️ Insert Image</a>"
        "<a href='%s/upload/photo-file/%s' style='background: #6f42c1; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📁 Upload File</a>"
        "<a href='%s/add-note/photo/%s' style='background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📝 Add Note</a>"
        "</div>"
        "</div>"
        
        "<div style='margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #ffc107;'>"
        "<strong>🆔 Upload ID Proof</strong><br/>"
        "<div style='margin-top: 8px;'>"
        "<a href='%s/upload/id-proof/%s' style='background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📁 Upload File</a>"
        "<a href='%s/upload/video/%s' style='background: #e83e8c; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>🎥 Insert Video</a>"
        "<a href='%s/add-note/id-proof/%s' style='background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📝 Add Note</a>"
        "</div>"
        "</div>"
        
        "<div style='margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #dc3545;'>"
        "<strong>📜 Upload Certifications</strong><br/>"
        "<div style='margin-top: 8px;'>"
        "<a href='%s/upload/certifications/%s' style='background: #007bff; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📁 Upload File</a>"
        "<a href='%s/add-note/certifications/%s' style='background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📝 Add Note</a>"
        "<a href='%s/numbered-list/certifications/%s' style='background: #fd7e14; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>🔢 Numbered List</a>"
        "</div>"
        "</div>"
        
        "<div style='margin-bottom: 15px; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #6f42c1;'>"
        "<strong>📄 Accept Offer Letter</strong><br/>"
        "<div style='margin-top: 8px;'>"
        "<a href='%s/add-note/offer-letter/%s' style='background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>📝 Add Note</a>"
        "<a href='%s/add-button/offer-letter/%s' style='background: #20c997; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>🔘 Add Button</a>"
        "<a href='%s/checklist/offer-letter/%s' style='background: #17a2b8; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 12px;'>✅ Checklist</a>"
        "</div>"
        "</div>"
        
        "</div>"
        
        "<div style='margin: 15px 0; padding: 10px; background-color: #e7f3ff; border-radius: 5px; border: 1px solid #b3d7ff;'>"
        "<strong>💡 How to use:</strong>"
        "<ul style='margin: 8px 0;'>"
        "<li>Click any button above to perform the action</li>"
        "<li>You'll be redirected to our secure portal</li>"
        "<li>Complete the required steps online</li>"
        "<li>All actions are tracked automatically</li>"
        "</ul>"
        "</div>"
        
        "<p><strong>Assignment Schedule:</strong></p>"
        "<ul>"
        "<li>Manager assignments: 0 days before plan date</li>"
        "<li>Employee assignments: 0-1 days before plan date</li>"
        "</ul>"
        
        "<p>Please proceed with the next steps as outlined above.</p>"
        "<p>We will contact you shortly with further instructions.</p>"
        "<p>Best regards,<br/>Recruitment Team</p>"
    ) % (
        (applicant.partner_name or 'Candidate'), 
        (applicant.job_id.name or ''),
        # Address Proof URLs
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        # Photo URLs
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        # ID Proof URLs
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        # Certifications URLs
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        # Offer Letter URLs
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token,
        'https://your-company-portal.com', applicant_token
    )

    # --- Collect attachments ---
    attachments_to_send = applicant.attachment_ids.sudo()  # direct attachments

    # Include attachments from chatter/messages
    for msg in applicant.message_ids.sudo():
        attachments_to_send |= msg.attachment_ids.sudo()

    # Copy attachments to mail.mail and collect ids
    attachment_list = []
    for attachment in attachments_to_send:
        attachment_copy = attachment.sudo().copy({
            'res_model': 'mail.mail',
            'res_id': False,
        })
        attachment_list.append(attachment_copy.id)

    # --- Create mail values ---
    mail_vals = {
        'subject': subject,
        'body_html': body,
        'email_to': applicant.email_from,
        'email_from': 'innosoultest@gmail.com',
        'model': 'hr.applicant',
        'res_id': applicant.id,
    }
    if attachment_list:
        mail_vals['attachment_ids'] = [(6, 0, attachment_list)]

    # Create and send email (use sudo to ensure permission)
    try:
        mail = env['mail.mail'].sudo().create(mail_vals)
        mail.sudo().send()
        
        # --- Move applicant to "Employee Created" stage ---
        employee_created_stage = env['hr.recruitment.stage'].search(
            [('name', '=', 'Employee Created')], limit=1
        )
        if employee_created_stage:
            applicant.sudo().write({'stage_id': employee_created_stage.id})

        # --- Log sent attachments in chatter ---
        attachment_names = ", ".join([att.name for att in attachments_to_send]) if attachments_to_send else "No attachments"

        applicant.sudo().message_post(
            body="✅ Employee Created email sent automatically with attachments: %s<br/>Stage moved to <b>Employee Created</b>.<br/>Interactive onboarding plan with clickable actions included in email." % attachment_names, 
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )
        
        _logger.info("Email with interactive onboarding sent successfully to %s", applicant.email_from)
        
    except Exception as e:
        _logger.error("Failed to send email to %s: %s", applicant.email_from, str(e))
        applicant.sudo().message_post(
            body="❌ Failed to send Employee Created email: %s" % str(e), 
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )