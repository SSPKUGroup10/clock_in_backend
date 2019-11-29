# -*- coding:utf-8 -*-
from datetime import datetime
from flask import current_app
from app.models import User
from app.utils import CN_DATETIME_FORMAT
from .base import WxTempNotifierBase, LINK_COLOR, FAILED_COLOR, NORMAL_COLOR, YOOQUN_COLOR


class WechatNotifier(WxTempNotifierBase):
    def yooqun_new_member(self, admin_openid, user):
        template = self.get_temp('yooqun_new_member')
        if template:
            count = self.session.query(User).count()
            title = '有新会员加入柚群, 目前会员总数为 {0}'.format(count)
            data = {
                'first': {
                    'value': title,
                    'color': LINK_COLOR
                },
                'keyword1': {
                    'value': '{name}\n用户ID: {id}'.format(name=user.nickname, id=user.id)
                },
                'keyword2': {
                    'value': user.created_at.strftime('%Y年%m月%d日 %H时%M分')
                },
                'remark': {
                    'value': '\n柚群运营团队'
                }
            }
            self.send_notification(admin_openid, template, data)

    def work_order_remind(self, admin_openid, type_name, user, desc, is_group=False):
        template = self.get_temp('work_order_remind')
        if template:
            data = {
                'first': {
                    'value': '您有一张新的工单，请及时处理',
                    'color': LINK_COLOR
                },
                'keyword1': {
                    'value': type_name
                },
                'keyword2': {
                    'value': user.fullname or user.nickname
                },
                'keyword3': {
                    'value': user.cell_phone
                },
                'keyword4': {
                    'value': user.city
                },
                'keyword5': {
                    'value': desc
                },
                'remark': {
                    'value': '\n柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}'.format(base_url=base_url, path='/myCreateEvent')
            if is_group:
                str_url = '{base_url}{path}{uuid}'.format(base_url=base_url, path='/groupDetails?groupUuid=', uuid=user.group_uuid)
            
            self.send_notification(admin_openid, template, data, url=str_url)

    def audit_result(self, user_openid, event, passed=True):
        template = self.get_temp('event_audit_result')
        if template:
            data = {
                'first': {
                    'value': '活动审核结果',
                    'color': LINK_COLOR
                },
                'keyword1': {
                    'value': event.title
                },
                'keyword2': {
                    'value': '审核{0}通过'.format('' if passed else '未'),
                    'color': '{0}'.format(NORMAL_COLOR if passed else FAILED_COLOR)
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}'.format(base_url=base_url, path='/myCreateEvent')
            self.send_notification(user_openid, template, data, url=str_url)

    def event_pay_success(self, user_openid, order):
        template = self.get_temp('event_pay_success')
        if template:
            title = '{user}({phone})已经报名您组织的活动，购买 {count} 张票，希望您及时和他取得联系，告知活动细节!' \
                .format(user=order.buyer_name, phone=order.buyer_phone, count=order.quantity)
            data = {
                'first': {
                    'value': title,
                    'color': LINK_COLOR
                },
                'keyword1': {
                    'value': str(int(order.amount / 100)) + '元'
                },
                'keyword2': {
                    'value': order.desc
                },
                'keyword3': {
                    'value': datetime.now().strftime('%Y年%m月%d日 %H时%M分')
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}'.format(base_url=base_url, path='/myEvent')
            self.send_notification(user_openid, template, data, url=str_url)

    def event_start_notification(self, member, event):
        template = self.get_temp('event_start_notification')
        if template:
            title = '您报名的活动 {event.title} 将于{time}开始，请提前到{event.location}签到' \
                .format(event=event, time=event.start_at.strftime(CN_DATETIME_FORMAT))

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'keyword1': {
                    'value': member.order_number
                },
                'keyword2': {
                    'value': member.desc
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}{uuid}'.format(base_url=base_url, path='/eventDetails?eventUuid=', uuid=event.uuid)
            self.send_notification(member.public_openid, template, data, url=str_url)

    def new_member(self, user_openid, group_uuid, member):
        template = self.get_temp('group_new_member')
        if template:
            data = {
                'first': {
                    'value': '恭喜您，有新成员加入您的社群！',
                    'color': LINK_COLOR
                },
                'keyword1': {
                    'value': '{name}({card_no})'.format(name=member.nickname, card_no=member.card_number)
                },
                'keyword2': {
                    'value': member.start_at.strftime('%Y年%m月%d日')
                },
                'remark': {
                    'value': '\n柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}{uuid}'.format(base_url=base_url, path='/groupDetails?groupUuid=', uuid=group_uuid)
            self.send_notification(user_openid, template, data, url=str_url)

    def event_change_notification(self, member, event):
        template = self.get_temp('event_start_notification')
        if template:
            title = '您报名的活动 {event.title} 有变更，将于 {time} 开始，请提前到 -{event.location}- 签到，如有疑问，请联系主办方' \
                .format(event=event, time=event.start_at.strftime(CN_DATETIME_FORMAT))

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'keyword1': {
                    'value': member.order_number
                },
                'keyword2': {
                    'value': member.desc
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            base_url = current_app.config['MOBILE_APP_URL']
            str_url = '{base_url}{path}{uuid}'.format(base_url=base_url, path='/eventDetails?eventUuid=', uuid=event.uuid)
            self.send_notification(member.public_openid, template, data, url=str_url)

    def new_withdraw_notification(self, admin_openid, nickname, withdraw_order):
        template = self.get_temp('new_withdraw_notification')
        if template:
            title = '有一笔提现待审核，请尽快审核'

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'keyword1': {
                    'value': nickname
                },
                'keyword2': {
                    'value': withdraw_order.created_at.strftime('%Y年%m月%d日')
                },
                'keyword3': {
                    'value': str(int(withdraw_order.amount / 100)) + '元'
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            self.send_notification(admin_openid, template, data, url='')

    def withdraw_success_notification(self, user_openid, nick_name, withdraw_amount, withdraw_time):
        template = self.get_temp('withdraw_success_notification')
        if template:
            title = '恭喜您{nick_name}，您已成功提现{withdraw_amount}元到您的微信账户！' \
                .format(nick_name=nick_name, withdraw_amount=withdraw_amount)

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'keyword1': {
                    'value': withdraw_amount
                },
                'keyword2': {
                    'value': withdraw_time
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            self.send_notification(user_openid, template, data, url='')

    def event_cancel_apply(self, user_openid, event_title, user_name, apply_reason):
        template = self.get_temp('event_cancel_apply')
        if template:
            title = '您发起的活动有一位朋友取消了报名。'

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'keyword1': {
                    'value': event_title
                },
                'keyword2': {
                    'value': user_name
                },
                'keyword3': {
                    'value': apply_reason
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            self.send_notification(user_openid, template, data, url='')

    def group_member_expired(self, user_open_id, member_name, group_member):
        template = self.get_temp('group_member_expired')
        if template:
            title = '您好，您的会员已到期，请您注意。'

            data = {
                'first': {
                    'value': title,
                    'color': YOOQUN_COLOR
                },
                'name': {
                    'value': member_name
                },
                'expDate': {
                    'value': group_member.expire_at
                },
                'remark': {
                    'value': '柚群运营团队'
                }
            }
            self.send_notification(user_open_id, template, data, url='')

