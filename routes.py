from flask import render_template, request, flash, redirect, url_for, jsonify, session
from app import app, db
from models import Family, Child
from forms import FamilyForm, ChildForm
from datetime import datetime
import logging
import os
from google_sheets_util import initialize_spreadsheet, add_family_to_spreadsheet

# Initialize the spreadsheet on startup
try:
    initialize_spreadsheet()
except Exception as e:
    logging.error(f"Failed to initialize Google Sheet: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    family_form = FamilyForm()
    
    if request.method == 'POST':
        # Get count of children from the form
        children_count = int(request.form.get('children_count', 0))
        
        # Create a new family record
        try:
            family = Family(
                head_name=request.form['head_name'],
                head_phone=request.form['head_phone'],
                spouse_name=request.form.get('spouse_name', ''),
                spouse_phone=request.form.get('spouse_phone', ''),
                address=request.form.get('address', ''),
                marital_status=request.form['marital_status']
            )
            db.session.add(family)
            db.session.flush()  # Flush to get the family ID
            
            # Only process children if there are any
            validation_passed = True
            
            if children_count > 0:
                # Process each child form
                for i in range(1, children_count + 1):
                    prefix = f'child_{i}'
                    
                    # Validate child form data
                    child_form = ChildForm(prefix=prefix)
                    child_form_data = {
                        'name': request.form.get(f'{prefix}-name'),
                        'date_of_birth': request.form.get(f'{prefix}-date_of_birth'),
                        'marital_status': request.form.get(f'{prefix}-marital_status', 'single')
                    }
                    
                    # Validate date format
                    try:
                        dob = datetime.strptime(child_form_data['date_of_birth'], '%Y-%m-%d').date()
                        
                        # Create child record
                        child = Child(
                            name=child_form_data['name'],
                            date_of_birth=dob,
                            marital_status=child_form_data['marital_status'],
                            family_id=family.id
                        )
                        db.session.add(child)
                    except ValueError:
                        flash(f"Invalid date format for Child {i}", "danger")
                        validation_passed = False
                    except Exception as e:
                        flash(f"Error processing Child {i}: {str(e)}", "danger")
                        validation_passed = False
            
            if validation_passed:
                db.session.commit()
                
                # Add the family data to Google Sheets
                try:
                    # Reload the family to get the child relationships
                    family = Family.query.get(family.id)
                    sheets_success = add_family_to_spreadsheet(family)
                    
                    if sheets_success:
                        flash("Family information saved successfully and added to Google Sheets!", "success")
                    else:
                        flash("Family information saved to database, but could not update Google Sheets.", "warning")
                except Exception as e:
                    logging.error(f"Error adding family to Google Sheets: {str(e)}")
                    flash("Family information saved, but there was an error updating Google Sheets.", "warning")
                
                return redirect(url_for('success', family_id=family.id))
            else:
                db.session.rollback()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving family data: {str(e)}")
            flash(f"Error saving family information: {str(e)}", "danger")
    
    return render_template('index.html', form=family_form)

@app.route('/success/<int:family_id>')
def success(family_id):
    family = Family.query.get_or_404(family_id)
    return render_template('success.html', family=family)

# Get admin password from environment variable
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
if not ADMIN_PASSWORD:
    logger.warning("No admin password set! Using default (not recommended for production)")
    ADMIN_PASSWORD = "admin123"

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            # Set a session variable to indicate admin is logged in
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('list_families'))
        else:
            flash("Invalid password", "danger")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("You have been logged out", "info")
    return redirect(url_for('index'))

@app.route('/families')
def list_families():
    # Check if admin is logged in
    if not session.get('admin_logged_in'):
        flash("You need to login as admin to view family records", "warning")
        return redirect(url_for('admin_login'))
    
    families = Family.query.order_by(Family.created_at.desc()).all()
    return render_template('families.html', families=families)

@app.route('/api/calculate-age', methods=['POST'])
def calculate_age():
    try:
        data = request.get_json()
        dob_str = data.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        today = datetime.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        return jsonify({'age': age})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
