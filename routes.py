from flask import render_template, request, flash, redirect, url_for, jsonify
from app import app, db
from models import Family, Child
from forms import FamilyForm, ChildForm
from datetime import datetime
import logging

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
                flash("Family information saved successfully!", "success")
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
