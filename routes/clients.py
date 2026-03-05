"""Client management routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from services.client_service import ClientService
from services.billing_service import BillingService
from services.payment_service import PaymentService
from services.mikrotik_service import MikrotikService
from config import Config

# Create blueprint for client routes
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


@clients_bp.route('/')
@login_required
def list_clients():
    """
    Display list of all clients with search/filter and connection status.
    
    Requirements: 2.2, 2.3
    """
    # Get search query and filters from request
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    
    # Build filters
    filters = {}
    if search_query:
        filters['search_query'] = search_query
    if status_filter:
        filters['status'] = status_filter
    
    # Get clients
    clients = ClientService.get_all_clients(filters if filters else None)
    
    # Get active users from Mikrotik to show connection status
    active_usernames = set()
    try:
        mikrotik = MikrotikService(
            host=Config.MIKROTIK_HOST,
            username=Config.MIKROTIK_USER,
            password=Config.MIKROTIK_PASSWORD
        )
        active_users = mikrotik.get_active_pppoe_users()
        active_usernames = {user['name'] for user in active_users}
    except Exception:
        # If Mikrotik fails, just show all as offline
        pass
    
    return render_template('clients/list.html', clients=clients, 
                         search_query=search_query, status_filter=status_filter,
                         active_usernames=active_usernames)


@clients_bp.route('/new', methods=['GET'])
@login_required
def new_client():
    """
    Display add client form.
    
    Requirements: 2.1
    """
    # Get available PPP profiles from Mikrotik
    profiles = []
    try:
        mikrotik = MikrotikService(
            host=Config.MIKROTIK_HOST,
            username=Config.MIKROTIK_USER,
            password=Config.MIKROTIK_PASSWORD
        )
        profiles = mikrotik.get_ppp_profiles()
    except Exception as e:
        flash(f'Warning: Could not load Mikrotik profiles: {str(e)}', 'warning')
        # Provide default profile if Mikrotik is unavailable
        profiles = [{'name': 'default', 'rate_limit': ''}]
    
    return render_template('clients/form.html', client=None, action='create', profiles=profiles)


@clients_bp.route('/', methods=['POST'])
@login_required
def create_client():
    """
    Create new client and PPPoE user in Mikrotik.
    
    Requirements: 2.1, 2.6
    """
    try:
        # Get form data
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'address': request.form.get('address', '').strip(),
            'contact_number': request.form.get('contact_number', '').strip(),
            'email': request.form.get('email', '').strip(),
            'pppoe_username': request.form.get('pppoe_username', '').strip(),
            'pppoe_password': request.form.get('pppoe_password', '').strip(),
            'mikrotik_profile': request.form.get('mikrotik_profile', 'default').strip(),
            'plan_name': request.form.get('plan_name', '').strip(),
            'plan_amount': request.form.get('plan_amount', '0'),
            'status': request.form.get('status', 'active')
        }
        
        # Create client (will also create PPPoE user in Mikrotik)
        client = ClientService.create_client(data)
        
        flash(f'Successfully added client: {client.full_name}', 'success')
        return redirect(url_for('clients.view_client', client_id=client.id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('clients.new_client'))
    except Exception as e:
        flash(f'Error creating client: {str(e)}', 'error')
        return redirect(url_for('clients.new_client'))


@clients_bp.route('/<int:client_id>')
@login_required
def view_client(client_id):
    """
    View client details with payment history and connection status.
    
    Requirements: 2.5, 8.1
    """
    # Get client
    client = ClientService.get_client(client_id)
    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('clients.list_clients'))
    
    # Get billing records
    bills = BillingService.get_client_bills(client_id)
    total_due = BillingService.calculate_total_due(client_id)
    
    # Get payment history
    payments = PaymentService.get_client_payments(client_id)
    total_paid = PaymentService.calculate_total_paid(client_id)
    
    # Check connection status from Mikrotik
    connection_status = 'offline'
    connection_details = None
    try:
        mikrotik = MikrotikService()
        user_info = mikrotik.get_user_by_name(client.pppoe_username)
        if user_info:
            connection_status = 'online'
            connection_details = user_info
    except Exception:
        # If Mikrotik fails, just show offline
        pass
    
    return render_template('clients/detail.html', 
                         client=client,
                         bills=bills,
                         total_due=total_due,
                         payments=payments,
                         total_paid=total_paid,
                         connection_status=connection_status,
                         connection_details=connection_details)


@clients_bp.route('/<int:client_id>/edit', methods=['GET'])
@login_required
def edit_client(client_id):
    """
    Display edit client form.
    
    Requirements: 2.4
    """
    client = ClientService.get_client(client_id)
    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('clients.list_clients'))
    
    # Get available PPP profiles from Mikrotik
    profiles = []
    try:
        mikrotik = MikrotikService(
            host=Config.MIKROTIK_HOST,
            username=Config.MIKROTIK_USER,
            password=Config.MIKROTIK_PASSWORD
        )
        profiles = mikrotik.get_ppp_profiles()
    except Exception as e:
        flash(f'Warning: Could not load Mikrotik profiles: {str(e)}', 'warning')
        # Provide default profile if Mikrotik is unavailable
        profiles = [{'name': 'default', 'rate_limit': ''}]
    
    return render_template('clients/form.html', client=client, action='edit', profiles=profiles)


@clients_bp.route('/<int:client_id>', methods=['POST'])
@login_required
def update_client(client_id):
    """
    Update client information.
    
    Requirements: 2.4
    """
    try:
        # Get form data
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'address': request.form.get('address', '').strip(),
            'contact_number': request.form.get('contact_number', '').strip(),
            'email': request.form.get('email', '').strip(),
            'pppoe_username': request.form.get('pppoe_username', '').strip(),
            'mikrotik_profile': request.form.get('mikrotik_profile', '').strip(),
            'plan_name': request.form.get('plan_name', '').strip(),
            'plan_amount': request.form.get('plan_amount', '0'),
            'status': request.form.get('status', 'active')
        }
        
        # Update client
        client = ClientService.update_client(client_id, data)
        
        flash(f'Successfully updated client: {client.full_name}', 'success')
        return redirect(url_for('clients.view_client', client_id=client.id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('clients.edit_client', client_id=client_id))
    except Exception as e:
        flash(f'Error updating client: {str(e)}', 'error')
        return redirect(url_for('clients.edit_client', client_id=client_id))


@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    """
    Delete client and their PPPoE user from Mikrotik.
    
    Requirements: 2.7
    """
    try:
        # Get client name before deletion
        client = ClientService.get_client(client_id)
        if not client:
            flash('Client not found.', 'error')
            return redirect(url_for('clients.list_clients'))
        
        client_name = client.full_name
        
        # Delete client (will also delete from Mikrotik)
        ClientService.delete_client(client_id)
        
        flash(f'Successfully deleted client: {client_name}', 'success')
        return redirect(url_for('clients.list_clients'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('clients.list_clients'))
    except Exception as e:
        flash(f'Error deleting client: {str(e)}', 'error')
        return redirect(url_for('clients.list_clients'))


@clients_bp.route('/sync', methods=['POST'])
@login_required
def sync_from_mikrotik():
    """
    Sync all PPPoE users from Mikrotik to database.
    
    Requirements: 2.8
    """
    try:
        result = ClientService.sync_from_mikrotik()
        
        if result['success']:
            message = f"Sync complete! Added: {result['added']}, Existing: {result['skipped']}"
            if result['errors'] > 0:
                message += f", Errors: {result['errors']}"
            flash(message, 'success')
        else:
            flash(f"Sync error: {result.get('error', 'Unknown error')}", 'error')
        
        return redirect(url_for('clients.list_clients'))
        
    except Exception as e:
        flash(f'Error syncing from Mikrotik: {str(e)}', 'error')
        return redirect(url_for('clients.list_clients'))


# API Endpoints for inline editing and disconnect

@clients_bp.route('/<int:client_id>/plan', methods=['PATCH'])
@login_required
def update_client_plan(client_id):
    """
    Update client plan (inline editing API endpoint).
    
    Expects JSON: {"plan_name": "...", "plan_amount": ...}
    
    Requirements: 1.2, 1.3
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate plan_name
        plan_name = data.get('plan_name', '').strip()
        if not plan_name:
            return jsonify({
                'success': False,
                'error': 'Plan name is required'
            }), 400
        
        if len(plan_name) > 100:
            return jsonify({
                'success': False,
                'error': 'Plan name must be 100 characters or less'
            }), 400
        
        # Validate plan_amount
        try:
            plan_amount = float(data.get('plan_amount', 0))
            if plan_amount <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Plan amount must be a positive number'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid plan amount'
            }), 400
        
        # Update client
        update_data = {
            'plan_name': plan_name,
            'plan_amount': plan_amount
        }
        
        client = ClientService.update_client(client_id, update_data)
        
        return jsonify({
            'success': True,
            'data': {
                'id': client.id,
                'plan_name': client.plan_name,
                'plan_amount': client.plan_amount
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error updating plan: {str(e)}'
        }), 500


@clients_bp.route('/<int:client_id>/disconnect', methods=['POST'])
@login_required
def disconnect_client(client_id):
    """
    Disconnect client's PPPoE session.
    
    Requirements: 4.4, 4.5
    """
    try:
        # Get client
        client = ClientService.get_client(client_id)
        if not client:
            return jsonify({
                'success': False,
                'error': 'Client not found'
            }), 404
        
        # Check if client has active session
        mikrotik = MikrotikService(
            host=Config.MIKROTIK_HOST,
            username=Config.MIKROTIK_USER,
            password=Config.MIKROTIK_PASSWORD
        )
        
        # Disconnect the session
        success = mikrotik.disconnect_pppoe_session(client.pppoe_username)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully disconnected {client.full_name}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Client is not currently connected or session not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error disconnecting client: {str(e)}'
        }), 500
