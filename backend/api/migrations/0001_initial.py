from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='InstituteDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255, unique=True)),
                ('verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('anonymous_handle', models.CharField(max_length=50, unique=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('institutional_verified', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('height_cm', models.IntegerField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('degree_or_profession', models.CharField(blank=True, max_length=255)),
                ('interests', models.JSONField(default=list)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(default='IN', max_length=2)),
                ('scope', models.CharField(choices=[('same_institute', 'Same Institute'), ('city', 'City'), ('state', 'State'), ('national', 'National'), ('global', 'Global')], default='same_institute', max_length=20)),
                ('preference_mode', models.CharField(choices=[('friend', 'Friend'), ('hookup', 'Hookup')], default='friend', max_length=10)),
                ('age_preference_min', models.IntegerField(default=18)),
                ('age_preference_max', models.IntegerField(default=35)),
                ('height_preference_min', models.IntegerField(blank=True, null=True)),
                ('height_preference_max', models.IntegerField(blank=True, null=True)),
                ('tokens', models.IntegerField(default=200)),
                ('active', models.BooleanField(default=True)),
                ('last_active', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('institute_domain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.institutedomain')),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked_at', models.DateTimeField(auto_now_add=True)),
                ('blocked_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to='api.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='api.user')),
            ],
            options={'unique_together': {('user', 'blocked_user')}},
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('match_mode', models.CharField(choices=[('friend', 'Friend'), ('hookup', 'Hookup')], max_length=10)),
                ('match_score', models.FloatField(default=0.0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('rejected', 'Rejected')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_initiated', to='api.user')),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_received', to='api.user')),
            ],
            options={'unique_together': {('user1', 'user2')}},
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('locked', 'Locked'), ('expired', 'Expired')], default='active', max_length=20)),
                ('message_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('locked_at', models.DateTimeField(blank=True, null=True)),
                ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_room', to='api.match')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('voice', 'Voice'), ('gift', 'Gift'), ('sticker', 'Sticker')], max_length=20)),
                ('content', models.TextField(blank=True)),
                ('media_url', models.URLField(blank=True)),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('seen', models.BooleanField(default=False)),
                ('seen_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='api.chatroom')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages_sent', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('price_inr', models.DecimalField(decimal_places=2, default=50, max_digits=10)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('payment_id', models.CharField(blank=True, max_length=255)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='api.chatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Sticker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sticker_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('image_url', models.URLField()),
                ('pack_name', models.CharField(max_length=100)),
                ('premium', models.BooleanField(default=False)),
                ('token_cost', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gift_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('animation_url', models.URLField()),
                ('premium', models.BooleanField(default=False)),
                ('token_cost', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('notification_type', models.CharField(choices=[('new_message', 'New Message'), ('match', 'Match'), ('payment_reminder', 'Payment Reminder'), ('chat_expiring', 'Chat Expiring'), ('chat_locked', 'Chat Locked')], max_length=30)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
                ('image_url', models.URLField(blank=True)),
                ('voice_url', models.URLField(blank=True)),
                ('read', models.BooleanField(default=False)),
                ('dismissible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='OtpToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=6, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('verified', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
            ],
        ),
    ]
